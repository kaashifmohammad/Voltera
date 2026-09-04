from datetime import datetime

from observations.historical_data_service import HistoricalDataService
from observations.observation import Observation


class HistoricalDataAccess:
    def __init__(self, service: HistoricalDataService):
        self.service = service

    def latest(self) -> Observation | None:
        return self.service.get_latest()

    def recent(self, count: int = 10) -> list[Observation]:
        return self.service.get_recent(count)

    def between(
        self,
        start: datetime,
        end: datetime,
    ) -> list[Observation]:
        return self.service.get_between(start, end)

    def count(self) -> int:
        return self.service.get_count()