from stress.scenarios import BatteryScenario
from stress.simulator import StressSimulator
from stress.validator import StressValidator


def test_simulation_result_counts_are_consistent():
    simulator = StressSimulator(
        lambda scenario: scenario.to_dict()
    )

    result = simulator.run(
        [
            BatteryScenario(100),
            BatteryScenario(75),
            BatteryScenario(50),
            BatteryScenario(25),
        ]
    )

    validator = StressValidator()

    assert validator.validate_completion(result)
    assert validator.validate_result_count(result)


def test_success_rate_is_consistent():
    simulator = StressSimulator(
        lambda scenario: scenario.to_dict()
    )

    result = simulator.run_repeated(
        BatteryScenario(50),
        100,
    )

    validator = StressValidator()

    assert validator.validate_success_rate(
        result,
        minimum=1.0,
    )


def test_validator_detects_failures():
    def runner(scenario):
        if scenario.battery_percent == 10:
            raise RuntimeError("failure")

        return scenario.to_dict()

    simulator = StressSimulator(runner)

    result = simulator.run(
        [
            BatteryScenario(50),
            BatteryScenario(10),
            BatteryScenario(50),
        ]
    )

    validator = StressValidator()

    assert validator.validate_completion(result)
    assert validator.validate_result_count(result)
    assert not validator.validate_no_unexpected_failures(
        result
    )


def test_stress_result_preserves_order():
    scenarios = [
        BatteryScenario(100),
        BatteryScenario(80),
        BatteryScenario(60),
        BatteryScenario(40),
        BatteryScenario(20),
    ]

    simulator = StressSimulator(
        lambda scenario: scenario.battery_percent
    )

    result = simulator.run(scenarios)

    assert result.results == [
        100,
        80,
        60,
        40,
        20,
    ]


def test_empty_stress_run_is_safe():
    simulator = StressSimulator(
        lambda scenario: scenario
    )

    result = simulator.run([])

    validator = StressValidator()

    assert result.total_cycles == 0
    assert result.successful_cycles == 0
    assert result.failed_cycles == 0
    assert result.results == []
    assert validator.validate_completion(result)


def test_zero_repetitions_are_safe():
    simulator = StressSimulator(
        lambda scenario: scenario
    )

    result = simulator.run_sequence(
        [BatteryScenario(50)],
        repetitions=0,
    )

    assert result.total_cycles == 0
    assert result.results == []