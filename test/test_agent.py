import unittest.mock as mock
import pandas as pd
from forta_agent import Log, TransactionEvent
from src.agent import handle_transaction, initialize, ASSETS, TRANSFER_EVENTS, get_coin_id_by_contract_address

def test_handle_transaction():
    # Mock the transaction_event and its filter_log function
    transaction_event = mock.MagicMock(spec=TransactionEvent)

    # Create sample transfer event data
    sample_transfer_event = {
        'block': {
            'timestamp': 1627651200
        },
        'price': 1.02
    }

    # Configure the mocked transaction_event.filter_log to return the sample_transfer_event
    transaction_event.filter_log.return_value = [sample_transfer_event]

    # Mock the get_coin_id_by_contract_address function to return a valid coin id
    get_coin_id_by_contract_address_mock = mock.Mock(return_value='usd-coin')
    with mock.patch('src.agent.get_coin_id_by_contract_address', get_coin_id_by_contract_address_mock):
        # Initialize the historical data and model
        initialize()

        # Mock the Prophet model and its functions to return a pre-defined forecast
        prophet_mock = mock.Mock()
        future_df = pd.DataFrame({
            'ds': pd.date_range('2023-04-17', periods=30, freq='D')
        })
        forecast_df = pd.DataFrame({
            'ds': pd.date_range('2023-04-17', periods=30, freq='D'),
            'yhat': [1.0] * 30
        })
        prophet_mock.predict.return_value = forecast_df
        with mock.patch('src.agent.Prophet', prophet_mock):
            # Call the handle_transaction function with the mocked transaction_event
            try:
                findings = handle_transaction(transaction_event)
            except Exception as e:
                # Print the exception for debugging purposes
                print(f"Error: {e}")
                # Re-raise the exception to fail the test
                raise e

            # Assertions for the expected behavior
            for asset in ASSETS:
                asset_key = asset.upper()
                assert findings[0]['name'] == f'{asset_key} Depeg Event'
                assert f'{asset_key} depeg detected with a predicted price of 1.02' in findings[0]['description']
                assert findings[0]['alert_id'] == f'FORTA-{asset_key}-DEPEG-1'
                assert findings[0]['severity'] == 2  # Medium severity
                assert findings[0]['type'] == 3  # Info type

                # Verify that filter_log was called with the correct arguments
                transaction_event.filter_log.assert_called_with(
                    TRANSFER_EVENTS[asset], ASSETS[asset]['address'])
