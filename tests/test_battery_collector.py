from collectors.battery.battery_collector import BatteryCollector


def test_battery_collector_returns_observation():
    collector = BatteryCollector()

    observation = collector.collect()

    assert observation is not None

    if observation.battery_percentage is not None:
        assert 0 <= observation.battery_percentage <= 100


def test_battery_collector_charging_status():
    collector = BatteryCollector()

    observation = collector.collect()

    assert observation.charging_status is None or isinstance(
        observation.charging_status, bool
    )


def test_battery_collector_time_left():
    collector = BatteryCollector()

    observation = collector.collect()

    assert observation.battery_time_left is None or isinstance(
        observation.battery_time_left, (int, float)
    )