import json
from pathlib import Path

from web3._utils.normalizers import normalize_abi
from web3.types import ABI


class Pomogator:
    @staticmethod
    def abi_from_file(path: Path) -> ABI:
        return normalize_abi(json.loads(open(path).read()))