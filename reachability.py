import logging
import cachetools

import config
__CONFIG = config.CONFIG[__name__]
__logger = logging.getLogger(__name__)

import kube

def generate_targets(nodes: dict):
    for node in nodes:
        pass