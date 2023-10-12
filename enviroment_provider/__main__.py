import rpyc


class ENVProviderService(rpyc.Service):
    def __init__(self) -> None:
        super(MainService, self).__init__()

    def on_connect(self, conn: rpyc.core.protocol.Connection):
        logging.info("Client connected.")

    def on_disconnect(self, conn):
        logging.info("Client disconnected.")

    def deactivate_pair(self, symbol: str) -> str:
        for exchange in self._active_settings_rconn.get_exchanges():
            self._active_settings_rconn.deactivate_ex_pair(exchange, symbol)
        return f"{symbol} deactivated"
