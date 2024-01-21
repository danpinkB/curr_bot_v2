from decimal import Decimal

from abstract.instrument import Instrument
from abstract.path_chain import PathChain, CLIQuoteUniswap, QuoteType

if __name__ == "__main__":
    path = PathChain.from_cli(
        CLIQuoteUniswap(
            "[V3] 80.00% = USDC -- 0.05% [0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640] --> WETH -- 0.3% [0x1d42064Fc4Beb5F8aAF85F4617AE8b3b5B8Bd801] --> UNI, [V3] 15.00% = USDC -- 0.01% [0x3416cF6C708Da44DB2624D63ea0AAef7113527C6] --> USDT -- 0.3% [0x3470447f3CecfFAc709D3e783A307790b0208d60] --> UNI, [V3] 5.00% = USDC -- 0.3% [0xD0fC8bA7E267f2bc56044A7715A489d851dC6D78] --> UNI",
            Decimal(0), Decimal(0), Decimal(0), "", 1
        ),
        Instrument.UNI__USDT,
        QuoteType.exactIn,
    )
    print(path)
