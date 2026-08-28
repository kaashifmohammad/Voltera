from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class BatteryScenario:
    """
    Represents one battery state used during stress testing.
    """

    battery_percent: float
    charging: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.battery_percent, (int, float)):
            raise ValueError("battery_percent must be numeric.")

        if not 0 <= self.battery_percent <= 100:
            raise ValueError(
                "battery_percent must be between 0 and 100."
            )

        if not isinstance(self.charging, bool):
            raise ValueError("charging must be boolean.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "battery_percent": self.battery_percent,
            "charging": self.charging,
        }


@dataclass(frozen=True)
class ContextScenario:
    """
    Represents a context/activity transition.
    """

    activity: str
    screen_active: bool = True
    idle: bool = False
    sleeping: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "activity": self.activity,
            "screen_active": self.screen_active,
            "idle": self.idle,
            "sleeping": self.sleeping,
        }


@dataclass(frozen=True)
class FailureScenario:
    """
    Represents an injected failure during stress testing.
    """

    stage: str
    cycle: int

    def __post_init__(self) -> None:
        if not isinstance(self.stage, str) or not self.stage.strip():
            raise ValueError("stage must be a non-empty string.")

        if self.cycle < 0:
            raise ValueError("cycle cannot be negative.")


@dataclass
class ScenarioSequence:
    """
    Collection of stress scenarios.
    """

    scenarios: list[Any] = field(default_factory=list)

    def add(self, scenario: Any) -> None:
        self.scenarios.append(scenario)

    def __iter__(self):
        return iter(self.scenarios)

    def __len__(self) -> int:
        return len(self.scenarios)