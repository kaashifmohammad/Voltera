import pytest

from observations.historical_intelligence import HistoricalIntelligence


class TestHistoricalIntelligence(HistoricalIntelligence):

    def get_latest(self):
        return None

    def get_recent(self, count=10):
        return []

    def get_between(self, start, end):
        return []

    def count(self):
        return 0


def test_historical_intelligence_is_abstract():
    assert HistoricalIntelligence is not None


def test_historical_intelligence_contract():
    intelligence = TestHistoricalIntelligence()

    assert intelligence.get_latest() is None
    assert intelligence.get_recent() == []
    assert intelligence.get_between(None, None) == []
    assert intelligence.count() == 0

from observations.observation_repository import ObservationRepository


def test_repository_implements_historical_intelligence(tmp_path):
    repository = ObservationRepository(
        file_path=tmp_path / "observations.csv"
    )

    assert isinstance(repository, HistoricalIntelligence)

from datetime import datetime, timedelta

from observations.historical_intelligence_adapter import (
    HistoricalIntelligenceAdapter,
)


def test_adapter_returns_latest():
    repository = ObservationRepository()
    adapter = HistoricalIntelligenceAdapter(repository)

    assert adapter.latest() == repository.get_latest()


def test_adapter_returns_recent():
    repository = ObservationRepository()
    adapter = HistoricalIntelligenceAdapter(repository)

    assert adapter.recent(5) == repository.get_recent(5)


def test_adapter_returns_between():
    repository = ObservationRepository()
    adapter = HistoricalIntelligenceAdapter(repository)

    end = datetime.now()
    start = end - timedelta(days=1)

    assert adapter.between(start, end) == repository.get_between(start, end)


def test_adapter_returns_total_count():
    repository = ObservationRepository()
    adapter = HistoricalIntelligenceAdapter(repository)

    assert adapter.total_observations() == repository.count()