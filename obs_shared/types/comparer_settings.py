from typing import NamedTuple, Tuple


class ComparerSettings(NamedTuple):
    percent: float
    delay_mills: int
    rvolume: int
    mdelay: int

    @staticmethod
    def keys() -> set[str]:
        return {"percent", "delay", "rvolume", "mdelay"}

    @staticmethod
    def from_row(row: Tuple[str, str, str, str]) -> 'ComparerSettings':
        return ComparerSettings(
            percent=float(row[0]),
            delay_mills=int(row[1]),
            rvolume=int(row[2]),
            mdelay=int(row[3])
        )

    def to_row(self) -> Tuple[str, str, str, str]:
        return str(self.percent), str(self.delay_mills), str(self.rvolume), str(self.mdelay)

