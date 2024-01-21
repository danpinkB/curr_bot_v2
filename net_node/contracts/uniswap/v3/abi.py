import os
from pathlib import Path

from net_node.contracts.pomogator import Pomogator

cwd = Path(os.path.dirname(os.path.abspath(__file__)))

FACTORY_ABI = Pomogator.abi_from_file(cwd/"static/factory.abi")
MIGRATOR_ABI = Pomogator.abi_from_file(cwd/"static/migrator.abi")
MULTICALL2_ABI = Pomogator.abi_from_file(cwd/"static/multicall2.abi")
NFT_POSITION_DESCRIPTOR_ABI = Pomogator.abi_from_file(cwd/"static/nft_position_descriptor.abi")
NFT_POSITION_ABI = Pomogator.abi_from_file(cwd / "static/nft_position.abi")
PERMIT_ABI = Pomogator.abi_from_file(cwd/"static/permit.abi")
POOL_ABI = Pomogator.abi_from_file(cwd/"static/pool.abi")
QUOTER_ABI = Pomogator.abi_from_file(cwd/"static/quoter.abi")
QUOTER_V2_ABI = Pomogator.abi_from_file(cwd/"static/quoterv2.abi")
ROUTER_ABI = Pomogator.abi_from_file(cwd/"static/router.abi")
ROUTER_V2_ABI = Pomogator.abi_from_file(cwd/"static/routerv2.abi")
TICK_LENS_ABI = Pomogator.abi_from_file(cwd/"static/tick_lens.abi")
UNIVERSAL_ROUTER_ABI = Pomogator.abi_from_file(cwd/"static/universal_router.abi")

