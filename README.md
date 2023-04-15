# USDC Depeg Detection Agent

## Description

This agent monitors USDC transactions to detect potential depegging events. It uses historical data and the Prophet library to forecast the future price of USDC. If the predicted price is outside the acceptable range, the agent generates a finding.

## Supported Chains

- Ethereum

## Alerts

- FORTA-USDC-DEPEG-1: USDC Depeg Event

## Test Data

To test this agent, you can use the provided unit tests which utilize mock objects to simulate transaction events that contain USDC transfers with prices outside the forecasted range.

To run the tests, execute the following command:

```bash
python -m unittest test_agent.py

```
