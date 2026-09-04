import pytest
from datetime import datetime, timedelta
from observations.observation_repository import ObservationRepository
from observations.historical_intelligence import HistoricalIntelligence
from observations.historical_intelligence_adapter import (
    HistoricalIntelligenceAdapter,
)
from observations.observation_factory import ObservationFactory
from observations.observation_store import ObservationStore

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

from observations.historical_data_service import HistoricalDataService


def test_service_returns_latest():
    repository = ObservationRepository()
    adapter = HistoricalIntelligenceAdapter(repository)
    service = HistoricalDataService(adapter)

    assert service.get_latest() == repository.get_latest()


def test_service_returns_recent():
    repository = ObservationRepository()
    adapter = HistoricalIntelligenceAdapter(repository)
    service = HistoricalDataService(adapter)

    assert service.get_recent(5) == repository.get_recent(5)


def test_service_returns_between():
    repository = ObservationRepository()
    adapter = HistoricalIntelligenceAdapter(repository)
    service = HistoricalDataService(adapter)

    start = datetime.now() - timedelta(days=1)
    end = datetime.now()

    assert service.get_between(start, end) == repository.get_between(
        start, end
    )


def test_service_returns_count():
    repository = ObservationRepository()
    adapter = HistoricalIntelligenceAdapter(repository)
    service = HistoricalDataService(adapter)

    assert service.get_count() == repository.count()

def test_service_uses_historical_intelligence_adapter():
    repository = ObservationRepository()
    adapter = HistoricalIntelligenceAdapter(repository)
    service = HistoricalDataService(adapter)

    assert service.adapter is adapter

class FakeHistoricalAdapter:
    def __init__(self):
        self.latest_called = False
        self.recent_called = False
        self.between_called = False
        self.count_called = False

    def latest(self):
        self.latest_called = True
        return None

    def recent(self, count=10):
        self.recent_called = True
        return []

    def between(self, start, end):
        self.between_called = True
        return []

    def total_observations(self):
        self.count_called = True
        return 0

def test_service_uses_adapter_boundary():
    adapter = FakeHistoricalAdapter()
    service = HistoricalDataService(adapter)

    assert service.get_latest() is None
    assert service.get_recent(5) == []
    assert service.get_between(None, None) == []
    assert service.get_count() == 0

    assert adapter.latest_called
    assert adapter.recent_called
    assert adapter.between_called
    assert adapter.count_called

from observations.historical_data_access import HistoricalDataAccess


def test_access_returns_latest():
    service = HistoricalDataService(
        HistoricalIntelligenceAdapter(ObservationRepository())
    )
    access = HistoricalDataAccess(service)

    assert access.latest() == service.get_latest()


def test_access_returns_recent():
    service = HistoricalDataService(
        HistoricalIntelligenceAdapter(ObservationRepository())
    )
    access = HistoricalDataAccess(service)

    assert access.recent(5) == service.get_recent(5)


def test_access_returns_between():
    service = HistoricalDataService(
        HistoricalIntelligenceAdapter(ObservationRepository())
    )
    access = HistoricalDataAccess(service)

    start = datetime.now() - timedelta(days=1)
    end = datetime.now()

    assert access.between(start, end) == service.get_between(start, end)


def test_access_returns_count():
    service = HistoricalDataService(
        HistoricalIntelligenceAdapter(ObservationRepository())
    )
    access = HistoricalDataAccess(service)

    assert access.count() == service.get_count()

class FakeHistoricalDataService:
    def __init__(self):
        self.latest_called = False
        self.recent_called = False
        self.between_called = False
        self.count_called = False

    def get_latest(self):
        self.latest_called = True
        return None

    def get_recent(self, count=10):
        self.recent_called = True
        return []

    def get_between(self, start, end):
        self.between_called = True
        return []

    def get_count(self):
        self.count_called = True
        return 0

def test_access_uses_service_boundary():
    service = FakeHistoricalDataService()
    access = HistoricalDataAccess(service)

    assert access.latest() is None
    assert access.recent(5) == []
    assert access.between(None, None) == []
    assert access.count() == 0

    assert service.latest_called
    assert service.recent_called
    assert service.between_called
    assert service.count_called

def test_end_to_end_historical_access(tmp_path):
    repository = ObservationRepository(
        file_path=tmp_path / "observations.csv"
    )

    observation = ObservationFactory.create(
        battery={
            "battery_percentage": 75.0,
            "charging_status": False,
            "battery_time_left": 3600.0,
        },
        system={
            "cpu_usage": 25.0,
            "ram_usage": 40.0,
            "active_application": "TestApp",
        },
    )

    ObservationStore(tmp_path / "observations.csv").save(observation)

    adapter = HistoricalIntelligenceAdapter(repository)
    service = HistoricalDataService(adapter)
    access = HistoricalDataAccess(service)

    latest = access.latest()

    assert latest is not None
    assert latest.battery_percentage == 75.0
    assert latest.cpu_usage == 25.0
    assert latest.ram_usage == 40.0
    assert latest.active_application == "TestApp"
    assert access.count() == 1

