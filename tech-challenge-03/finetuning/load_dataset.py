import asyncio
import itertools
import json
import logging

import coloredlogs
from pysqlx_engine import PySQLXEnginePool

from .const import TEST_FILE, TRAIN_FILE

logging.basicConfig(level=logging.INFO)
coloredlogs.install(level="INFO")

# Database connection URI
uri = "postgresql://test:test@localhost:5432/test"

files = [TRAIN_FILE, TEST_FILE]

pool = PySQLXEnginePool(uri=uri, min_size=100, max_size=101)
BATCH_SIZE_FILE = 1000
BATCH_SIZE_INSERT = 100

semaphore = asyncio.Semaphore(BATCH_SIZE_INSERT)


def read_json_in_batches(file_path: str, batch_size: str):
    with open(file_path, "r") as f:
        count = 0
        while True:
            batch = list(itertools.islice(f, batch_size))
            if not batch:
                break
            count += 1
            yield [json.loads(line) for line in batch]


# {"uid": "0000032069", "title": "Adult Ballet Tutu Cheetah Pink", "content": ""}
async def create_table():
    async with pool.connection() as conn:
        SQL = """
            CREATE TABLE IF NOT EXISTS product (
                id SERIAL PRIMARY KEY,
                uid VARCHAR(255),
                title TEXT,
                content TEXT
            );
        """
        SQL_IDX = "CREATE INDEX IF NOT EXISTS idx_product_title ON product (title);"

        await conn.execute(SQL)
        await conn.execute(SQL_IDX)


async def insert_data(data: list):
    SQL = "INSERT INTO product (uid, title, content) VALUES (:uid, :title, :content);"

    async with semaphore:
        async with pool.connection() as conn:
            await conn.start_transaction()
            for row in data:
                await conn.execute(sql=SQL, parameters=row)

            await conn.commit()


def create_batch_insert(data, batch_size):
    values = []
    for idx in range(0, len(data), batch_size):
        values.append(data[idx : idx + batch_size])

    return values


async def load_data(data: list):
    process = [insert_data(row) for row in data]
    await asyncio.gather(*process)


async def main():
    await pool.start()
    logging.info("Pool started")
    await create_table()
    for file_path in files:
        logging.info(f"Processing file {file_path}")
        count_lines = 0
        for data in read_json_in_batches(file_path, BATCH_SIZE_FILE):
            batch_data = create_batch_insert(data, BATCH_SIZE_INSERT)
            await load_data(data=batch_data)
            count_lines += len(data)
            logging.info(f"Batch loaded {count_lines}")

    logging.info("Data loaded")
    await pool.stop()


if __name__ == "__main__":
    # fixed
    asyncio.get_event_loop().run_until_complete(main())
    # asyncio.run(main())
