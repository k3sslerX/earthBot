from typing import Union

import asyncpg
from asyncpg.pool import Pool

from data import config


class Database:
    def __init__(self):
        self.__pool: Union[Pool, None] = None

    async def get_pool(self):
        await self.__create_connection()
        return self.__pool

    async def __create_connection(self):
        self.__pool = self.__pool or await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False):
        pool = await self.get_pool()
        async with pool.acquire() as connection:
            if fetch:
                result = await connection.fetch(command, *args)
            elif fetchval:
                result = await connection.fetchval(command, *args)
            elif fetchrow:
                result = await connection.fetchrow(command, *args)
            elif execute:
                result = await connection.execute(command, *args)
        return result

    async def select_value(self, sql):
        return await self.execute(sql, fetchval=True)

    async def select_list(self, sql):
        return await self.execute(sql, fetch=True)

    async def execute_table(self, sql):
        return await self.execute(sql, execute=True)

    async def create_users_table(self):
        sql = 'CREATE TABLE IF NOT EXISTS earth_users (member BIGINT, cash INT, stones INT, messages INT, hours INT, minutes INT)'
        return await self.execute(sql, execute=True)

db = Database()
