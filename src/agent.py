import pandas as pd
from prophet import Prophet
from pycoingecko import CoinGeckoAPI
from forta_agent import Finding, FindingType, FindingSeverity
from datetime import datetime, timedelta

# Constants
TRANSFER_EVENTS = {
    'USDC': '{"name":"Transfer","type":"event","anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}]}',
    'Tether': '{"name":"Transfer","type":"event","anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}]}',
    'DAI': '{"name":"Transfer","type":"event","anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}]}',
    'stakedETH': '{"name":"Transfer","type":"event","anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}]}',
    'WBTC': '{"name":"Transfer","type":"event","anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}]}',
}

ASSETS = {
    'usdc': '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
    'tether': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
    'dai': '0x6B175474E89094C44Da98b954EedeAC495271d0F',
    'staked_eth': '0x00',  # Replace with actual staked ETH derivatives contract address
    'wbtc': '0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599'
}

DEPEG_THRESHOLD = 0.01
PRICE_HISTORY_DAYS = 30

# Global variables
historical_data = []
cg = CoinGeckoAPI()
model = None
forecast = None


def initialize():
    global historical_data, model, forecast

    # Fetch historical price data for each asset
    for asset in ASSETS:
        historical_data[asset] = fetch_asset_price_history(
            ASSETS[asset], PRICE_HISTORY_DAYS)

    # Initialize dictionaries to store models and forecasts for each asset
    model = {}
    forecast = {}

    # Train the Prophet model for each asset and make predictions
    for asset in ASSETS:
        # Prepare the data for Prophet
        data = historical_data[asset].reset_index().rename(
            columns={'timestamp': 'ds', 'price': 'y'})

        # Train the Prophet model
        model[asset] = Prophet(yearly_seasonality=True)
        model[asset].fit(data)

        # Make predictions
        future = model[asset].make_future_dataframe(periods=1, freq='H')
        forecast[asset] = model[asset].predict(future)


def fetch_asset_price_history(asset_address, days):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    asset_data = cg.get_coin_market_chart_range_by_contract_address(
        id='ethereum',
        contract_address=asset_address,
        vs_currency='usd',
        from_timestamp=int(start_date.timestamp()),
        to_timestamp=int(end_date.timestamp())
    )

    price_data = asset_data['prices']
    df = pd.DataFrame(price_data, columns=['timestamp', 'price'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df


def fetch_pool_data(asset_address):
    uniswap_base_url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"
    query = """
    {{
      pairs(first: 1, where: {{token0: "{asset_address}"}}) {{
        id
        token0 {{
          symbol
          name
        }}
        token1 {{
          symbol
          name
        }}
        reserve0
        reserve1
        reserveUSD
        totalSupply
        trackedReserveETH
        token0Price
        token1Price
        volumeToken0
        volumeToken1
        volumeUSD
      }}
    }}
    """.format(asset_address=asset_address)

    response = requests.post(uniswap_base_url, json={'query': query})
    data = response.json()

    if 'data' in data and 'pairs' in data['data']:
        return data['data']['pairs'][0]
    else:
        return None


def analyze_asset_depeg(asset, events):
    global historical_data, model, forecast

    # Create a DataFrame from the asset transfer events
    event_data = []
    for event in events:
        timestamp = datetime.fromtimestamp(event['block']['timestamp'])
        event_data.append({'ds': timestamp, 'y': event['price']})

    df = pd.DataFrame(event_data)

    # Append the historical data
    combined_data = historical_data[asset].append(df)

    # Train a time series model using Prophet
    model[asset].fit(combined_data)

    # Predict the future price
    future = model[asset].make_future_dataframe(periods=1)
    forecast[asset] = model[asset].predict(future)

    # Check if the predicted price is within the DEPEG_THRESHOLD
    last_row = forecast[asset].iloc[-1]
    predicted_price = last_row['yhat']
    lower_bound = last_row['yhat_lower']
    upper_bound = last_row['yhat_upper']

    if abs(predicted_price - 1) > DEPEG_THRESHOLD or lower_bound > 1 or upper_bound < 1:
        return True, predicted_price
    else:
        return False, predicted_price


def handle_transaction(transaction_event):
    findings = []

    # Loop through each asset and analyze for depeg events
    for asset in ASSETS:
        # Filter the transaction logs for asset transfers
        asset_transfer_event_abi = TRANSFER_EVENTS[asset]
        asset_address = ASSETS[asset]['address']
        asset_transfer_events = transaction_event.filter_log(
            asset_transfer_event_abi, asset_address)

        # Analyze the asset transfers for depeg events
        depeg_detected, predicted_price = analyze_asset_depeg(
            asset, asset_transfer_events)

        if depeg_detected:
            findings.append(Finding({
                'name': f'{asset} Depeg Event',
                'description': f'{asset} depeg detected with a predicted price of {predicted_price}',
                'alert_id': f'FORTA-{asset}-DEPEG-1',
                'severity': FindingSeverity.Medium,
                'type': FindingType.Info
            }))

    return findings
