from datetime import datetime

from observations.historical_intelligence_adapter import (
    HistoricalIntelligenceAdapter,
)
from observations.observation import Observation


class HistoricalDataService:
    def __init__(self, adapter: HistoricalIntelligenceAdapter):
        self.adapter = adapter

    def get_latest(self) -> Observation | None:
        return self.adapter.latest()

    def get_recent(self, count: int = 10) -> list[Observation]:
        return self.adapter.recent(count)

    def get_between(
        self,
        start: datetime,
        end: datetime,
    ) -> list[Observation]:
        return self.adapter.between(start, end)

    def get_count(self) -> int:
        return self.adapter.total_observations()