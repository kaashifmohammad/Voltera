from stress.scenarios import BatteryScenario
from stress.simulator import StressSimulator


def test_battery_discharge_sequence():
    scenarios = [
        BatteryScenario(100),
        BatteryScenario(90),
        BatteryScenario(75),
        BatteryScenario(50),
        BatteryScenario(30),
        BatteryScenario(20),
        BatteryScenario(10),
        BatteryScenario(5),
    ]

    observed = []

    simulator = StressSimulator(
        lambda scenario: observed.append(
            scenario.battery_percent
        )
    )

    result = simulator.run(scenarios)

    assert result.successful_cycles == len(scenarios)
    assert observed == [
        100,
        90,
        75,
        50,
        30,
        20,
        10,
        5,
    ]


def test_charging_transition():
    scenarios = [
        BatteryScenario(10, False),
        BatteryScenario(15, True),
        BatteryScenario(25, True),
        BatteryScenario(50, True),
        BatteryScenario(75, True),
        BatteryScenario(100, True),
    ]

    simulator = StressSimulator(
        lambda scenario: scenario.to_dict()
    )

    result = simulator.run(scenarios)

    assert result.successful_cycles == 6
    assert all(
        item["charging"]
        for item in result.results[1:]
    )


def test_charge_discharge_charge_cycle():
    scenarios = [
        BatteryScenario(50, False),
        BatteryScenario(40, False),
        BatteryScenario(30, False),
        BatteryScenario(30, True),
        BatteryScenario(50, True),
        BatteryScenario(70, True),
        BatteryScenario(70, False),
        BatteryScenario(60, False),
    ]

    simulator = StressSimulator(
        lambda scenario: scenario.to_dict()
    )

    result = simulator.run(scenarios)

    assert result.total_cycles == 8
    assert result.failed_cycles == 0