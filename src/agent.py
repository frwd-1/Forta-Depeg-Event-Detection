print("start agent")
import forta_agent
import pandas as pd
import asyncio
from prophet import Prophet
from pycoingecko import CoinGeckoAPI
from forta_agent import (
    Finding,
    FindingType,
    FindingSeverity,
    TransactionEvent,
    get_json_rpc_url,
)
from datetime import datetime
from .ogconstants import ASSETS, PRICE_HISTORY_DAYS, DEPEG_THRESHOLD, TRANSFER_EVENTS
import src.ogutils


# Global variables
historical_data = {}
cg = CoinGeckoAPI()
model = None
forecast = None
json_rpc_url = get_json_rpc_url()
print("JSON RPC URL:", json_rpc_url)
print("before startup function")


async def initialize():
    await print("initializing")
    global historical_data, model, forecast
    # Fetch historical price data for each asset
    for asset in ASSETS:
        historical_data[asset] = src.ogutils.fetch_asset_price_history(
            ASSETS[asset], PRICE_HISTORY_DAYS
        )

    # Initialize dictionaries to store models and forecasts for each asset
    model = {}
    forecast = {}

    # Train the Prophet model for each asset and make predictions
    for asset in ASSETS:
        # Prepare the data for Prophet
        data = (
            historical_data[asset]
            .reset_index()
            .rename(columns={"timestamp": "ds", "price": "y"})
        )

        # Train the Prophet model
        model[asset] = Prophet(yearly_seasonality=True)
        model[asset].fit(data)

        # Make predictions
        future = model[asset].make_future_dataframe(periods=1, freq="H")
        forecast[asset] = model[asset].predict(future)


print("before analyze asset depeg")


def analyze_asset_depeg(asset, events):
    global historical_data, model, forecast

    # Create a DataFrame from the asset transfer events
    event_data = []
    for event in events:
        timestamp = datetime.fromtimestamp(event["block"]["timestamp"])
        event_data.append({"ds": timestamp, "y": event["price"]})

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
    predicted_price = last_row["yhat"]
    lower_bound = last_row["yhat_lower"]
    upper_bound = last_row["yhat_upper"]

    if abs(predicted_price - 1) > DEPEG_THRESHOLD or lower_bound > 1 or upper_bound < 1:
        return True, predicted_price
    else:
        return False, predicted_price


print("before analyze transaction")


def analyze_transaction(
    transaction_event: forta_agent.transaction_event.TransactionEvent,
):
    findings = []

    # Loop through each asset and analyze for depeg events
    for asset in ASSETS:
        # Filter the transaction logs for asset transfers
        asset_transfer_event_abi = TRANSFER_EVENTS[asset]
        asset_address = ASSETS[asset]
        asset_transfer_events = transaction_event.filter_log(
            asset_transfer_event_abi, asset_address
        )

        # Analyze the asset transfers for depeg events
        depeg_detected, predicted_price = analyze_asset_depeg(
            asset, asset_transfer_events
        )

        if depeg_detected:
            findings.append(
                Finding(
                    {
                        "name": f"{asset} Depeg Event",
                        "description": f"{asset} depeg detected with a predicted price of {predicted_price}",
                        "alert_id": f"FORTA-{asset}-DEPEG-1",
                        "severity": FindingSeverity.Medium,
                        "type": FindingType.Info,
                    }
                )
            )

    return findings


print("before main")


async def main(event: forta_agent.transaction_event.TransactionEvent):
    print("running main")
    return asyncio.run(analyze_transaction(event))


def provide_handle_transaction():
    """
    This function is just a wrapper for the handle_transaction()
    @return:
    """

    def wrapped_handle_transaction(
        transaction_event: forta_agent.transaction_event.TransactionEvent,
    ) -> list:
        return [
            finding
            for findings in asyncio.run(main(transaction_event))
            for finding in findings
        ]

    return wrapped_handle_transaction


real_handle_transaction = provide_handle_transaction()

print("before handle transaction")


def handle_transaction(
    transaction_event: TransactionEvent,
):
    print("running handle_transaction")
    """
    This function is used by Forta SDK
    @param transaction_event: forta_agent.transaction_event.TransactionEvent
    @return:
    """
    return real_handle_transaction(transaction_event)


print("end of agent")
# if __name__ == "__main__":
#     # Create a dummy TransactionEvent object
#     print("creating dummy tx")
#     dummy_transaction_event = TransactionEvent(
#         {
#             "transaction": {
#                 "hash": "",
#                 "from": "",
#                 "to": "",
#                 "value": "",
#                 "nonce": "",
#                 "gas": "",
#                 "gas_price": "",
#                 "input": "",
#             },
#             "receipt": {
#                 "gas_used": "",
#                 "status": "",
#                 "logs": [],
#             },
#             "block": {
#                 "number": "",
#                 "hash": "",
#                 "timestamp": "",
#             },
#         }
#     )

#     # Call the function(s) you want to test here, passing the dummy TransactionEvent object
#     handle_transaction(dummy_transaction_event)
