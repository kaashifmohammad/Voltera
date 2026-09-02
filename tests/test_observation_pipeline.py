from datetime import datetime

from observations.observation import Observation
from observations.observation_pipeline import ObservationPipeline


def create_observation():
    return Observation(
        timestamp=datetime(2026, 9, 2, 12, 0, 0),
        battery_percentage=75,
        charging_status=False,
        battery_time_left=3600,
        cpu_usage=20.5,
        ram_usage=60.2,
        active_application="TestApp",
    )


def test_pipeline_processes_valid_observation(tmp_path):
    store_path = tmp_path / "observations.csv"

    from observations.observation_store import ObservationStore

    store = ObservationStore(store_path)
    pipeline = ObservationPipeline(store)

    observation = create_observation()
    result = pipeline.process(observation)

    assert result == observation
    assert store_path.exists()


def test_pipeline_persists_observation(tmp_path):
    store_path = tmp_path / "observations.csv"

    from observations.observation_store import ObservationStore

    store = ObservationStore(store_path)
    pipeline = ObservationPipeline(store)

    pipeline.process(create_observation())

    content = store_path.read_text(encoding="utf-8")

    assert "75" in content
    assert "TestApp" in content