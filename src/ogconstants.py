print("importing constants...")
TRANSFER_EVENTS = {
    "usdc": '{"name":"Transfer","type":"event","anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}]}',
    "tether": '{"name":"Transfer","type":"event","anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}]}',
    "dai": '{"name":"Transfer","type":"event","anonymous":false,"inputs":[{"indexed":true,"name":"src","type":"address"},{"indexed":true,"name":"dst","type":"address"},{"indexed":false,"name":"wad","type":"uint256"}]}',
    "stakedeth": '{"name":"Transfer","type":"event","anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}]}',
    "wbtc": '{"name":"Transfer","type":"event","anonymous":false,"inputs":[{"indexed":true,"name":"from","type":"address"},{"indexed":true,"name":"to","type":"address"},{"indexed":false,"name":"value","type":"uint256"}]}',
}

ASSETS = {
    "usdc": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "tether": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
    "dai": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
    "staked_eth": "0x00",  # Replace with actual staked ETH derivatives contract address
    "wbtc": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
}

DEPEG_THRESHOLD = 0.01
PRICE_HISTORY_DAYS = 30


print("completed constants import")
