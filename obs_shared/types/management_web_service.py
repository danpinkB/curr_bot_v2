from abc import ABC, abstractmethod
from typing import Optional


class MainServiceBase(ABC):
    @abstractmethod
    def deactivate_pair(self, *args, **kwargs) -> Optional[str]:
        pass

    @abstractmethod
    def activate_pair(self, *args, **kwargs) -> Optional[str]:
        pass

    @abstractmethod
    def deactivate_exchange_pair(self, *args, **kwargs) -> Optional[str]:
        pass

    @abstractmethod
    def activate_exchange_pair(self, *args, **kwargs) -> Optional[str]:
        pass

    @abstractmethod
    def get_ex_banned_pairs(self, *args, **kwargs) -> Optional[str]:
        pass

    @abstractmethod
    def get_price(self, *args, **kwargs) -> Optional[str]:
        pass

    @abstractmethod
    def get_exchange_price(self, *args, **kwargs) -> Optional[str]:
        pass

    @abstractmethod
    def get_exchanges(self, *args, **kwargs) -> Optional[str]:
        pass

