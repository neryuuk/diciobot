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


def post(word: str, content) -> str:
    comandos = [
        'definir',
        'sinonimos',
        'antonimos',
        'exemplos',
        'conjugar',
        'rimas',
        'anagramas',
    ]

    if not word or len(word) == 0:
        return None

    if not content:
        return None

    result = {}

    for i, comando in enumerate(comandos):
        result[comando] = content[i]

    conn.json().set(word, Path.root_path(), result)

    return content
