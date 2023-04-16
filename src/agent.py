import pandas as pd
from prophet import Prophet
from pycoingecko import CoinGeckoAPI
from forta_agent import Finding, FindingType, FindingSeverity
from datetime import datetime, timedelta

# Constants
USDC_TRANSFER_EVENT = '{"name":"Transfer","type":"event","anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}]}'
USDC_ADDRESS = '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48'
DEPEG_THRESHOLD = 0.01
PRICE_HISTORY_DAYS = 30

# Global variables
historical_data = []
cg = CoinGeckoAPI()
model = None
forecast = None


def initialize():
    global historical_data, model, forecast

    # Fetch historical USDC price data
    days = 30
    historical_data = fetch_usdc_price_history(days)

    # Prepare the data for Prophet
    historical_data.reset_index(inplace=True)
    historical_data = historical_data.rename(
        columns={'timestamp': 'ds', 'price': 'y'})

    # Train the Prophet model
    model = Prophet(yearly_seasonality=True)
    model.fit(historical_data)

    # Make predictions
    future = model.make_future_dataframe(periods=1, freq='H')
    forecast = model.predict(future)


def fetch_usdc_price_history(days):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    usdc_data = cg.get_coin_market_chart_range_by_id(
        id='usd-coin',
        vs_currency='usd',
        from_timestamp=int(start_date.timestamp()),
        to_timestamp=int(end_date.timestamp())
    )

    price_data = usdc_data['prices']
    df = pd.DataFrame(price_data, columns=['timestamp', 'price'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df


def analyze_usdc_depeg(events):
    global historical_data, model, forecast

    # Create a DataFrame from the USDC transfer events
    event_data = []
    for event in events:
        timestamp = datetime.fromtimestamp(event['block']['timestamp'])
        event_data.append({'ds': timestamp, 'y': event['price']})

    df = pd.DataFrame(event_data)

    # Append the historical data
    combined_data = historical_data.append(df)

    # Train a time series model using Prophet
    model.fit(combined_data)

    # Predict the future price
    future = model.make_future_dataframe(periods=1)
    forecast = model.predict(future)

    # Check if the predicted price is within the DEPEG_THRESHOLD
    last_row = forecast.iloc[-1]
    predicted_price = last_row['yhat']
    lower_bound = last_row['yhat_lower']
    upper_bound = last_row['yhat_upper']

    if abs(predicted_price - 1) > DEPEG_THRESHOLD or lower_bound > 1 or upper_bound < 1:
        return True, predicted_price
    else:
        return False, predicted_price


def handle_transaction(transaction_event):
    findings = []

    # Filter the transaction logs for any USDC transfers
    usdc_transfer_events = transaction_event.filter_log(
        USDC_TRANSFER_EVENT, USDC_ADDRESS)

    # Analyze the USDC transfers for depeg events
    depeg_detected, predicted_price = analyze_usdc_depeg(usdc_transfer_events)

    if depeg_detected:
        findings.append(Finding({
            'name': 'USDC Depeg Event',
            'description': f'USDC depeg detected with a predicted price of {predicted_price}',
            'alert_id': 'FORTA-USDC-DEPEG-1',
            'severity': FindingSeverity.Medium,
            'type': FindingType.Info
        }))

    return findings
