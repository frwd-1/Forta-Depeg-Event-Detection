# from pycoingecko import CoinGeckoAPI
# import pandas as pd
# import requests

# cg = CoinGeckoAPI()

# def fetch_asset_price_history(asset_address, days):

#     # Get the coin ID using the contract address
#     coin_id = get_coin_id_by_contract_address(asset_address)

#     if coin_id is None:
#         raise ValueError(f"Unable to find coin with contract address {asset_address}")

#     asset_data = cg.get_coin_market_chart_by_id(
#         id=coin_id,
#         vs_currency='usd',
#         days=days
#     )

#     price_data = asset_data['prices']
#     df = pd.DataFrame(price_data, columns=['timestamp', 'price'])
#     df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
#     df.set_index('timestamp', inplace=True)
#     return df

# def get_coin_id_by_contract_address(contract_address):
#     coins = cg.get_coins_list()
#     for coin in coins:
#         if coin.get('contract_address') == contract_address.lower():
#             return coin['id']
#     return None

# def fetch_pool_data(asset_address):
#     uniswap_base_url = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"
#     query = """
#     {{
#       pairs(first: 1, where: {{token0: "{asset_address}"}}) {{
#         id
#         token0 {{
#           symbol
#           name
#         }}
#         token1 {{
#           symbol
#           name
#         }}
#         reserve0
#         reserve1
#         reserveUSD
#         totalSupply
#         trackedReserveETH
#         token0Price
#         token1Price
#         volumeToken0
#         volumeToken1
#         volumeUSD
#       }}
#     }}
#     """.format(asset_address=asset_address)

#     response = requests.post(uniswap_base_url, json={'query': query})
#     data = response.json()

#     if 'data' in data and 'pairs' in data['data']:
#         return data['data']['pairs'][0]
#     else:
#         return None