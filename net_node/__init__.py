import json
import os

cwd = os.path.dirname(os.path.abspath(__file__))
# factory_abi = json.loads(open(cwd+'/static/factory.json').read())
# pair_abi = json.loads(open(cwd+'/static/pair_abi.json').read())
erc_20_abi = json.loads(open(cwd + '/erc20_abi.json').read())
# pool_abi = json.loads(open(cwd+'/static/pool_abi.json').read())
# factory_abi_v3 = json.loads(open(cwd+'/static/factory_abi_v3.json').read())
uni_v2_router_abi = json.loads(open(cwd + '/uni_v2_router_abi.json').read())
uni_v3_quoter_abi = json.loads(open(cwd + '/uni_v3_quoter_abi.json').read())
