from stress.scenarios import BatteryScenario
from stress.simulator import StressSimulator
from stress.validator import StressValidator


def test_long_sequence_completes():
    simulator = StressSimulator(
        lambda scenario: {
            "battery": scenario.battery_percent
        }
    )

    scenario = BatteryScenario(75)

    result = simulator.run_repeated(
        scenario,
        100,
    )

    assert result.total_cycles == 100
    assert result.successful_cycles == 100
    assert result.failed_cycles == 0


def test_many_cycles_preserve_result_count():
    simulator = StressSimulator(
        lambda scenario: scenario.to_dict()
    )

    result = simulator.run_repeated(
        BatteryScenario(50),
        500,
    )

    assert len(result.results) == 500


def test_long_run_success_rate_is_stable():
    simulator = StressSimulator(
        lambda scenario: scenario.to_dict()
    )

    result = simulator.run_repeated(
        BatteryScenario(80),
        1000,
    )

    assert result.success_rate == 1.0


def test_repeated_sequence():
    simulator = StressSimulator(
        lambda scenario: scenario.to_dict()
    )

    scenarios = [
        BatteryScenario(100, True),
        BatteryScenario(75),
        BatteryScenario(50),
        BatteryScenario(25),
        BatteryScenario(10),
    ]

    result = simulator.run_sequence(
        scenarios,
        repetitions=100,
    )

    assert result.total_cycles == 500
    assert result.successful_cycles == 500