from dotenv import load_dotenv
from os import getenv
from redis import ConnectionPool, Redis
from redis.commands.json.path import Path

load_dotenv()

pool = ConnectionPool(
    host=getenv('REDIS_HOST'),
    port=getenv('REDIS_PORT'),
    username=getenv('REDIS_USER'),
    password=getenv('REDIS_PASS'),
    db=0,
)
conn = Redis(connection_pool=pool)


def get(word: str):
    if not word:
        return None

    if len(word) == 0:
        return None

    content = conn.json().get(word)
    return content
