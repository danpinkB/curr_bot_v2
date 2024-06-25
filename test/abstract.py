import unittest
from _decimal import Decimal

import web3

from abstract.exchange import Exchange
from abstract.instrument import Instrument
from message_broker.topics.notification import ExchangeInstrumentDifference

web3_conn = web3.Web3(web3.HTTPProvider("http://srv22130.dus4.fastwebserver.de:8545"))


class MyTestCase(unittest.TestCase):
    def __init__(self, methodName: str):
        super().__init__(methodName)
    # test ExchangeInstrumentDifference

    def test(self) -> None:
        model = ExchangeInstrumentDifference(
            instrument=Instrument.ARB__USDT,
            buy_exchange=Exchange.UNISWAP,
            sell_exchange=Exchange.BINANCE,
            buy_price=Decimal("10.1"),
            sell_price=Decimal("10.4")
        )
        bytes_ = model.to_bytes()
        self.assertEquals(bytes_, ExchangeInstrumentDifference.from_bytes(bytes_).to_bytes())


if __name__ == '__main__':
    unittest.main()
