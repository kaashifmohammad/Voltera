from stress.scenarios import ContextScenario
from stress.simulator import StressSimulator


def test_active_idle_sleep_wake_sequence():
    scenarios = [
        ContextScenario(
            "active",
            screen_active=True,
        ),
        ContextScenario(
            "idle",
            screen_active=True,
            idle=True,
        ),
        ContextScenario(
            "sleep",
            screen_active=False,
            idle=True,
            sleeping=True,
        ),
        ContextScenario(
            "wake",
            screen_active=True,
            idle=False,
            sleeping=False,
        ),
        ContextScenario(
            "active",
            screen_active=True,
        ),
    ]

    observed = []

    simulator = StressSimulator(
        lambda scenario: observed.append(
            scenario.activity
        )
    )

    result = simulator.run(scenarios)

    assert result.successful_cycles == 5
    assert observed == [
        "active",
        "idle",
        "sleep",
        "wake",
        "active",
    ]


def test_context_changes_do_not_break_cycles():
    scenarios = [
        ContextScenario("coding"),
        ContextScenario("browsing"),
        ContextScenario("video"),
        ContextScenario("gaming"),
        ContextScenario("idle"),
        ContextScenario("meeting"),
    ]

    simulator = StressSimulator(
        lambda scenario: scenario.to_dict()
    )

    result = simulator.run_sequence(
        scenarios,
        repetitions=50,
    )

    assert result.total_cycles == 300
    assert result.failed_cycles == 0


def test_screen_transitions_are_preserved():
    scenarios = [
        ContextScenario(
            "active",
            screen_active=True,
        ),
        ContextScenario(
            "idle",
            screen_active=False,
            idle=True,
        ),
        ContextScenario(
            "wake",
            screen_active=True,
        ),
    ]

    simulator = StressSimulator(
        lambda scenario: scenario.screen_active
    )

    result = simulator.run(scenarios)

    assert result.results == [
        True,
        False,
        True,
    ]