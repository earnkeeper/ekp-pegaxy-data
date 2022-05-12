import asyncio
import itertools
import json
import time
from email.policy import default

import aiohttp
from aiolimiter import AsyncLimiter
from aioretry import RetryInfo, RetryPolicyStrategy, retry
from decouple import config
from sqlalchemy import select
from db.pg_db import PgDb

class ParsePegas:
    PROXY_HOST = config("PROXY_HOST", default=None)
    PROXY_PORT = config("PROXY_PORT", default=3128, cast=int)
    API_BASE_URL = 'https://api-apollo.pegaxy.io/v1/game-api/pega/'

    def __init__(self):
        self.pg_db = PgDb()
        self.http_req_per_sec = 30
        self.db_page_size = 50
        self.limiter = AsyncLimiter(self.http_req_per_sec, time_period=1)



    @staticmethod
    def retry_policy(info: RetryInfo):
        print(info.exception)
        return False, (info.fails - 1) % 10 + 1

    @retry(retry_policy)
    async def parse_from_api(self, pega_id):
        pega_url = self.API_BASE_URL + str(pega_id)

        async with aiohttp.ClientSession() as session:

            await self.limiter.acquire()

            print(pega_url)

            if self.PROXY_HOST is not None:
                response = await session.get(url=pega_url, proxy=f"http://{self.PROXY_HOST}:{self.PROXY_PORT}")
            else:
                response = await session.get(url=pega_url)

            if response.status != 200:
                raise Exception(f"Response code: {response.status}")

            text = await response.read()

            if text == "Too many requests, please try again later.":
                raise Exception(f"Response code: 429")

            data = json.loads(text.decode())

            pega_info = {
                'name': data['pega']['name'],
                'father_id': data['pega']['fatherId'],
                'mother_id': data['pega']['motherId'],
                'gender': data['pega']['gender'],
                'bloodline': data['pega']['bloodLine'],
                'avatar_id_1': data['pega']['design']['avatar'].split('/')[-1],
                'avatar_id_2': data['pega']['design']['avatar_2'].split('/')[-1]
            }

            print(f"Updating pega id {pega_id} in the database")

            self.pg_db.update_query(pega_id=pega_id, pega_info=pega_info)

    async def parse_pegas(self):
        while True:
            print(f"Fetching new pega ids from database")

            # list_of_ids = get_data_from_db(pg_db)
            list_of_ids = self.pg_db.get_rows_with_null(self.db_page_size)
            print(f"Processing {len(list_of_ids)} pega ids")

            if not list_of_ids:
                break

            await asyncio.gather(*[self.parse_from_api(pega_id) for pega_id in list_of_ids])


