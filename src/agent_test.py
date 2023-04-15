import unittest
from unittest.mock import MagicMock
from forta_agent import FindingSeverity, FindingType
from agent import handle_transaction


class TestAgent(unittest.TestCase):

    def test_handle_transaction(self):
        # Mock a transaction_event object
        mock_transaction_event = MagicMock()

        # Mock filter_log function
        mock_transaction_event.filter_log.return_value = [
            {
                'block': {
                    'timestamp': 1677649420  # Mocked timestamp
                },
                'price': 0.99  # Mocked price outside the forecasted range
            }
        ]

        # Mock analyze_usdc_depeg function
        analyze_usdc_depeg_mock = MagicMock()
        # Mocked depeg_detected and predicted_price
        analyze_usdc_depeg_mock.return_value = (True, 0.99)

        # Replace the original function with the mocked function
        with unittest.mock.patch('your_bot_module.analyze_usdc_depeg', analyze_usdc_depeg_mock):
            findings = handle_transaction(mock_transaction_event)

        # Check if there is exactly one finding generated
        self.assertEqual(len(findings), 1)

        # Verify the finding's properties
        finding = findings[0]
        self.assertEqual(finding.name, 'USDC Depeg Event')
        self.assertEqual(
            finding.description, 'USDC depeg detected with a predicted price of 0.99')
        self.assertEqual(finding.alert_id, 'FORTA-USDC-DEPEG-1')
        self.assertEqual(finding.severity, FindingSeverity.Medium)
        self.assertEqual(finding.type, FindingType.Info)


if __name__ == '__main__':
    unittest.main()
