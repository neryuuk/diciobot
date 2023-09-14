import redis
from dotenv import load_dotenv
from os import getenv
load_dotenv()

conn = redis.Redis(
    host=getenv('REDIS_HOST'),
    port=getenv('REDIS_PORT'),
    password=getenv('REDIS_PASS'),
)
