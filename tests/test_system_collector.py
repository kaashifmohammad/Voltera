from collectors.system.system_collector import SystemCollector


def test_system_collector_returns_observation():
    collector = SystemCollector()

    observation = collector.collect()

    assert observation is not None
    assert 0 <= observation.cpu_usage <= 100
    assert 0 <= observation.ram_usage <= 100


def test_system_collector_active_application():
    collector = SystemCollector()

    observation = collector.collect()

    assert isinstance(observation.active_application, str)
    assert observation.active_application != ""