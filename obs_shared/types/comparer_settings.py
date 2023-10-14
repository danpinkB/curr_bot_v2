from typing import NamedTuple, Tuple


class ComparerSettings(NamedTuple):
    percent: float
    delay: float
    rvolume: int
    mdelay: float

    @staticmethod
    def keys() -> set[str]:
        return {"percent", "delay", "rvolume", "mdelay"}

    @staticmethod
    def from_row(row: Tuple[str, str, int, str]) -> 'ComparerSettings':
        return ComparerSettings(
            percent=float(row[0]),
            delay=float(row[1]),
            rvolume=row[2],
            mdelay=float(row[0])
        )

    def to_row(self) -> Tuple[str, str, int, str]:
        return str(self.percent), str(self.delay), self.rvolume, str(self.mdelay)

