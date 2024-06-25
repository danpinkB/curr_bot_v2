import json

import requests

PROVIDER_ENDPOINT = "https://mainnet.infura.io/v3/f7d97b0dc2cc4cacbe0ce490110745b6"

response = requests.post(
    url=PROVIDER_ENDPOINT,
    data=json.dumps({
        'jsonrpc': '2.0',
        'method': 'eth_getBlockByNumber',
        'params': [
            'latest',
            True,
        ],
        "id": 1
    })
)
data = response.json()['result']
# print(data)
for tx in data['transactions']:
    print(tx)
    print()