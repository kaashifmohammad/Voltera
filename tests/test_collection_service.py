from observations.collection_service import CollectionService


def test_collection_service_collects_and_stores(tmp_path):
    from observations.observation_store import ObservationStore
    from observations.observation_pipeline import ObservationPipeline

    store_path = tmp_path / "observations.csv"

    store = ObservationStore(store_path)
    pipeline = ObservationPipeline(store)
    service = CollectionService(pipeline=pipeline)

    observation = service.collect_and_store()

    assert observation is not None
    assert store_path.exists()


def test_collection_service_persists_real_observation(tmp_path):
    from observations.observation_store import ObservationStore
    from observations.observation_pipeline import ObservationPipeline

    store_path = tmp_path / "observations.csv"

    store = ObservationStore(store_path)
    pipeline = ObservationPipeline(store)
    service = CollectionService(pipeline=pipeline)

    service.collect_and_store()

    content = store_path.read_text(encoding="utf-8")

    assert "timestamp" in content
    assert "cpu_usage" in content
    assert "ram_usage" in content