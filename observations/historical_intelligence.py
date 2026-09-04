from abc import ABC, abstractmethod
from datetime import datetime

from observations.observation import Observation


class HistoricalIntelligence(ABC):

    @abstractmethod
    def get_latest(self) -> Observation | None:
        pass

    @abstractmethod
    def get_recent(self, count: int = 10) -> list[Observation]:
        pass

    @abstractmethod
    def get_between(
        self,
        start: datetime,
        end: datetime,
    ) -> list[Observation]:
        pass

    @abstractmethod
    def count(self) -> int:
        pass