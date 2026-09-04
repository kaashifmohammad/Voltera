from datetime import datetime

from observations.historical_intelligence import HistoricalIntelligence
from observations.observation import Observation


class HistoricalIntelligenceAdapter:
    def __init__(self, source: HistoricalIntelligence):
        self.source = source

    def latest(self) -> Observation | None:
        return self.source.get_latest()

    def recent(self, count: int = 10) -> list[Observation]:
        return self.source.get_recent(count)

    def between(
        self,
        start: datetime,
        end: datetime,
    ) -> list[Observation]:
        return self.source.get_between(start, end)

    def total_observations(self) -> int:
        return self.source.count()