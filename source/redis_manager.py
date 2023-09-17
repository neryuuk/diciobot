from dotenv import load_dotenv
from os import getenv
from redis import ConnectionPool, Redis
from redis.commands.json.path import Path

load_dotenv()

COMMANDS = [
    'definir',
    'sinonimos',
    'antonimos',
    'exemplos',
    'conjugar',
    'rimas',
    'anagramas',
]

pool = ConnectionPool(
    host=getenv('REDIS_HOST'),
    port=getenv('REDIS_PORT'),
    username=getenv('REDIS_USER'),
    password=getenv('REDIS_PASS'),
    db=0,
)
conn = Redis(connection_pool=pool)


def get(word: str, option: str = None):
    if not word or len(word) == 0:
        return None

    content = conn.json().get(word)
    if not content:
        return None

    if option and option in COMMANDS:
        return [content[option]]

    resultado = []
    for _, value in content.items():
        resultado.append(value)

    return resultado


def post(word: str, content, option: str = None) -> str:
    if not word or len(word) == 0:
        return None

    if not content:
        return None

    result = {}

    for i, command in enumerate(COMMANDS):
        result[command] = content[i]

    conn.json().set(word, Path.root_path(), result)

    if option and option in COMMANDS:
        return [result[option]]

    return content
