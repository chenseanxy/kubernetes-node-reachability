import cachetools
from kubernetes import kubernetes
import logging

import config
__CONFIG = config.CONFIG["kube"]
__logger = logging.getLogger("kube")

@cachetools.cached(cachetools.TTLCache(1, __CONFIG["NODE_META_TTL"]))
def get_nodes():
    kubernetes.config.load_kube_config()
    kube_api = kubernetes.client.CoreV1Api()
    nodes = kube_api.list_node().items
    return nodes

def get_node_ips():
    nodes = get_nodes()
    result = {}
    for node in nodes:
        name = node.metadata.name

        # Get first InternalIP off every node
        addr = None
        for endpoint in node.status.addresses:
            if endpoint.type == "InternalIP":
                addr = endpoint.address
        
        if not addr:
            __logger.warn(f"Node {name} has no InternalIP: {node.status.addresses}")
            continue
        
        result[name] = addr
    return result

if __name__ == "__main__":
    print(get_node_ips())