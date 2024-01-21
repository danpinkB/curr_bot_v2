import os
from pathlib import Path
from net_node.contracts.pomogator import Pomogator

cwd = Path(os.path.dirname(os.path.abspath(__file__)))

FACTORY_ABI = Pomogator.abi_from_file(cwd/"static/factory.abi")
PAIR_ABI = Pomogator.abi_from_file(cwd/"static/pair.abi")
ROUTER_ABI = Pomogator.abi_from_file(cwd/"static/router.abi")
