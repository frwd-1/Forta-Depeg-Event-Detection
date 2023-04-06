class DBUtils:
    def __init__(self):
        self.swaps = None
        self.base = None
        self.future = None
        self.pools = None

    # getter methods that return the values of the corresponding instance variables
    # self is a special keyword in python that refers to the instance of the class that is being operated on
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
        # Assuming that 'asset' column is in the 'pools' table
        rows = await self.pools.get_all_rows_by_criteria({'asset': asset})
        pool_contracts = [row['pool_contract'] for row in rows]
        return pool_contracts


db_utils = DBUtils()
