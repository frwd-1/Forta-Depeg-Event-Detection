from forta_agent import Finding, FindingType, FindingSeverity
import requests
import json

# Define monitored assets
ASSETS = {
    "USDC": {
        "address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "decimals": 6
    },
    "USDT": {
        "address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "decimals": 6
    },
    "DAI": {
        "address": "0x6b175474e89094c44da98b954eedeac495271d0f",
        "decimals": 18
    },
    "stETH": {
        "address": "0xae7ab96520de3a18e5e111b5eaab095312d7fe84",
        "decimals": 18
    },
    "WBTC": {
        "address": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",
        "decimals": 8
    },
}

# ERC20 Transfer event
ERC20_TRANSFER_EVENT = '{"name":"Transfer","type":"event","anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}]}'

findings_count = 0

# Fetch asset prices from CoinGecko


def get_asset_prices():
    ids = ','.join([asset.lower() for asset in ASSETS.keys()])
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd"
    response = requests.get(url)
    return json.loads(response.text)


def fetch_pool_data(asset_address):
    url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
    query = """
    {
      pools(where: {token0: $token, token1: $token}) {
        id
        token0 {
          symbol
        }
        token1 {
          symbol
        }
        sqrtPrice
        tick
        liquidity
        volumeUSD
      }
    }
    """
    variables = {
        "token": asset_address.lower()
    }
    response = requests.post(
        url, json={'query': query, 'variables': variables})
    data = response.json()

    if "data" in data and "pools" in data["data"]:
        return data["data"]["pools"]
    else:
        return []


# Example usage
eth_usdc_pool_data = fetch_pool_data(
    "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")  # USDC address
print(eth_usdc_pool_data)


def handle_transaction(transaction_event):
    global findings_count
    findings = []

    # Limit the agent to emit only 5 findings to avoid spamming the alert feed
    if findings_count >= 5:
        return findings

    asset_prices = get_asset_prices()

    for asset, asset_data in ASSETS.items():
        asset_transfer_events = transaction_event.filter_log(
            ERC20_TRANSFER_EVENT, asset_data['address'])

        for transfer_event in asset_transfer_events:
            to = transfer_event['args']['to']
            from_ = transfer_event['args']['from']
            value = transfer_event['args']['value']
            normalized_value = value / (10 ** asset_data['decimals'])

            # Check if more than 10,000 USD worth of the asset was transferred
            if normalized_value * asset_prices[asset.lower()]['usd'] > 10000:
                findings.append(Finding({
                    'name': f'High {asset} Transfer',
                    'description': f'High amount of {asset} transferred: {normalized_value}',
                    'alert_id': f'FORTA-{asset}-TRANSFER',
                    'severity': FindingSeverity.Low,
                    'type': FindingType.Info,
                    'metadata': {
                        'to': to,
                        'from': from_,
                    }
                }))
                findings_count += 1

                # Fetch pool data for the asset
                fetch_pool_data(asset_data['address'])

    return findings


class FortaAgent:
    def __init__(self):
        pass

    def get_metadata(self):
        return {
            'alert_id': 'FORTA-ALERT-DETECTION',
            'name': 'Forta Detection Agent',
            'author': 'YourName',
            'version': '0.0.1',
            'description': 'Detects suspicious transfers of specified assets',
        }

    def check_transaction(self, transaction_event):
        return handle_transaction(transaction_event)


def test():
    # Write test cases for your agent here
    pass


if __name__ == "__main__":
    test()
