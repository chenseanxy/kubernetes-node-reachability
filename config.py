import os
import yaml
import dotenv
dotenv.load_dotenv()
import logging

CONF_PATH=os.getenv("CONF_PATH") or "./config.yml"

def __load_config():
    with open(CONF_PATH, "r") as f:
        conf = yaml.load(f, Loader=yaml.SafeLoader)
    return conf

CONFIG = __load_config()

logging.basicConfig()
