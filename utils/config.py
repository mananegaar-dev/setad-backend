from pathlib import Path


def loadenv() -> None:
    """
    Return .env file Path
    

    usage:
    ```
        from dotenv import load_dotenv
        from os import getenv
        from utils.config import loadenv

        load_dotenv(loadenv()) 

        REDIS_HOST = getenv("REDIS_HOST", "redis")
    ```
    """
    DIR = Path(__file__).resolve().parent.parent

    ENV_PATH = DIR /".env"

    return ENV_PATH

