import ast
import logging
from typing import NamedTuple, Tuple, Dict, List

from obs_shared.types.token_row import TokenRow


class PathRowChain(NamedTuple):
    token_from: TokenRow
    token_to: TokenRow
    fee: int

    type_ = Tuple[TokenRow.type_, TokenRow.type_, int]

    @staticmethod
    def from_row(row: Tuple[TokenRow.type_, TokenRow.type_, int]) -> 'PathRowChain':
        return PathRowChain(
            token_from=TokenRow.from_row(row[0]),
            token_to=TokenRow.from_row(row[1]),
            fee=row[2]
        )

    @staticmethod
    def from_string(data: str) -> "PathRowChain":
        return PathRowChain.from_row(ast.literal_eval(data))

    def to_string(self) -> str:
        return str(self.to_row())

    def to_row(self) -> Tuple[TokenRow.type_, TokenRow.type_, int]:
        return self.token_from.to_row(), self.token_to.to_row(), self.fee


class PathRow(NamedTuple):
    chains: Dict[str, List[PathRowChain]]

    @staticmethod
    def from_row(row: Dict[str, List[PathRowChain.type_]]) -> 'PathRow':
        return PathRow(
            chains={amount: [PathRowChain.from_row(path_chain) for path_chain in chain_elements] for amount, chain_elements in row.items()}
        )

    @staticmethod
    def from_string(data: str) -> "PathRow":
        return PathRow.from_row(ast.literal_eval(data))

    def __iter__(self):
        for chain in self.chains.values():
            yield chain

    def to_string(self) -> str:
        return str(self.to_row())

    def to_row(self) -> Dict[str, List[PathRowChain.type_]]:
        chain_entity: PathRowChain
        chain_amount: str
        return {amount: [chain_entity.to_row() for chain_entity in chain_entities] for amount, chain_entities in self.chains.items()}
