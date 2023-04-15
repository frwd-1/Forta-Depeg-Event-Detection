from sqlalchemy import Table


class DBUtils:
    def __init__(self):
        self.swaps = None
        self.base = None
        self.future = None
        self.pools = None

    def get_swaps(self):
        return self.swaps

    def get_pools(self):
        return self.pools

    def get_future(self):
        return self.future

    def set_tables(self, swaps, pools, future):
        self.swaps = swaps
        self.pools = pools
        self.future = future

    def set_base(self, base):
        self.base = base

    async def get_pool_contracts_by_asset(self, asset: str):
        rows = await self.pools.get_all_rows_by_criteria({'asset': asset})
        pool_contracts = [row['pool_contract'] for row in rows]
        return pool_contracts

    def set_swaps(self, swaps_table: Table):
        self.swaps = swaps_table

    def set_pools(self, pools_table: Table):
        self.pools = pools_table

    def set_future(self, future_table: Table):
        self.future = future_table


db_utils = DBUtils()
