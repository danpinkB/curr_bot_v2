import os
from pathlib import Path

from net_node.contracts.pomogator import Pomogator

cwd = Path(os.path.dirname(os.path.abspath(__file__)))

ERC20_ABI = Pomogator.abi_from_file(cwd/"erc20_abi.json")
