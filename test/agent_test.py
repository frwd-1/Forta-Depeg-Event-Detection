import eth_abi
import pytest

from src.db.controller import init_async_db
from src.db import db_utils
from forta_agent import FindingSeverity, create_transaction_event, create_block_event
from web3 import Web3
from eth_utils import keccak, encode_hex

from src.agent import provide_handle_transaction, provide_handle_block
from src.utils import get_protocols_by_chain

FREE_ETH_ADDRESS = "0xE0dD882D4dA747e9848D05584e6b42c6320868be"
protocols = get_protocols_by_chain(1)
protocols_addresses = list(
    map(lambda x: Web3.toChecksumAddress(x).lower(), protocols.values()))
SWAP = "Swap(address,address,int256,int256,uint160,uint128,int24)"


def swap_event(amount0, amount1, address_):
    hash = keccak(text=SWAP)
    data = eth_abi.encode_abi(["int256", "int256", "uint160", "uint128", "int24"], [
                              amount0, amount1, 1, 1, 1])
    data = encode_hex(data)
    address1 = eth_abi.encode_abi(["address"], [FREE_ETH_ADDRESS])
    address1 = encode_hex(address1)
    address2 = eth_abi.encode_abi(["address"], [FREE_ETH_ADDRESS])
    address2 = encode_hex(address2)
    topics = [hash, address1, address2]
    return {'topics': topics,
            'data': data,
            'address': address_}


class TestDepegEventAgent:

    async def setup(self):
        swaps, pools, future = await init_async_db(test=True)
        db_utils.set_tables(swaps, pools, future)

    def test_high_usdc_price_movement_alert(self):

        # Create a sample transaction event with a high USDC price movement
        tx_event = create_transaction_event({
            'transaction': {
                'from': FREE_ETH_ADDRESS,
                'to': FREE_ETH_ADDRESS,
            },
            'block': {
                'number': 14506125,
                'timestamp': 1648894338,
            },
            'logs': [swap_event(1000000000000, 1, "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")]
        })

        # Call the handle_transaction function and check if there is a finding related to USDC
        findings = provide_handle_transaction()(tx_event)
        assert len(findings) > 0, "No findings detected in handle_transaction"

        usdc_alert_triggered = False
        for finding in findings:
            if "USDC" in finding["name"]:
                usdc_alert_triggered = True
                break

        assert usdc_alert_triggered, "High USDC price movement alert not triggered in handle_transaction"
