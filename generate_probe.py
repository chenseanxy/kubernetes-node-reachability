import yaml

import kube

def generate_probe(ip: str, hostname: str, all_ips: list):
    return {
        'metadata': {
            'name': f'probe-{hostname}',
            'namespace': 'monitoring'
        }, 
        'spec': {
            'jobName': 'monitoring/reachability',
            'interval': '1s',
            'module': 'tcp_connect',
            'prober': {
                'url': f'{ip}:19115', 
                'scheme': 'http',
                'path': '/probe'
            },
            'targets': {
                'staticConfig': {
                    'static': [f"{addr}:19115" for addr in all_ips], 
                    'labels': {'source': f'{ip}'},
                    'relabelingConfigs': [
                        {
                            'sourceLabels': ['__param_target'],
                            'targetLabel': 'target',
                            'regex': '(.*):19115',
                            'replacement': '$1',
                        }
                    ]
                }
            },
        }
    }


def generate_probe_list():
    nodes = kube.get_node_ips()
    return {
        'apiVersion': 'monitoring.coreos.com/v1', 
        'kind': 'ProbeList',
        'items': [
            generate_probe(ip, hostname, nodes.values()) 
            for hostname, ip in nodes.items()
        ]
    }

with open("./manifests/probe.yml", "w") as f:
    yaml.dump(generate_probe_list(), f)
