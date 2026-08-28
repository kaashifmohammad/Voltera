from stress.scenarios import BatteryScenario
from stress.simulator import StressSimulator


def test_failure_does_not_stop_following_cycles():
    calls = []

    def runner(scenario):
        calls.append(scenario.battery_percent)

        if scenario.battery_percent == 20:
            raise RuntimeError("injected failure")

        return scenario.to_dict()

    scenarios = [
        BatteryScenario(50),
        BatteryScenario(30),
        BatteryScenario(20),
        BatteryScenario(10),
        BatteryScenario(5),
    ]

    simulator = StressSimulator(runner)
    result = simulator.run(scenarios)

    assert result.total_cycles == 5
    assert result.successful_cycles == 4
    assert result.failed_cycles == 1
    assert calls == [50, 30, 20, 10, 5]


def test_repeated_failures_are_contained():
    def runner(scenario):
        if scenario.battery_percent < 20:
            raise RuntimeError("failure")

        return scenario.to_dict()

    scenarios = [
        BatteryScenario(50),
        BatteryScenario(10),
        BatteryScenario(5),
        BatteryScenario(15),
        BatteryScenario(40),
    ]

    result = StressSimulator(runner).run(
        scenarios
    )

    assert result.total_cycles == 5
    assert result.successful_cycles == 2
    assert result.failed_cycles == 3


def test_failure_result_contains_error_information():
    def runner(_):
        raise ValueError("expected failure")

    result = StressSimulator(runner).run(
        [BatteryScenario(50)]
    )

    assert result.failed_cycles == 1
    assert result.results[0]["error"] == (
        "expected failure"
    )


def test_recovery_after_failure():
    state = {"failed": False}

    def runner(scenario):
        if not state["failed"]:
            state["failed"] = True
            raise RuntimeError("first failure")

        return scenario.to_dict()

    simulator = StressSimulator(runner)

    result = simulator.run(
        [
            BatteryScenario(50),
            BatteryScenario(50),
            BatteryScenario(50),
        ]
    )

    assert result.failed_cycles == 1
    assert result.successful_cycles == 2