import os

from dotenv import load_dotenv


def load_env():
    if os.getenv('environment_type') == 'production':
        env_file_path = '../env/.env.production'
    else:
        env_file_path = '../env/.env.development'

    dotenv_path = os.path.join(os.path.dirname(__file__), env_file_path)
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
