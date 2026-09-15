from dataclasses import dataclass
from typing import Optional

from observations.battery_discharge import (
    BatteryDischarge,
    DischargeSession,
)
from observations.historical_data_access import HistoricalDataAccess


@dataclass(frozen=True)
class HeavyUsageResult:
    """Represents one historically heavy battery usage session."""

    session: DischargeSession
    drain_rate: float
    excess_drain_rate: float


@dataclass(frozen=True)
class HeavyUsageDetectionResult:
    """Historical battery sessions identified as unusually heavy usage."""

    session_count: int
    average_drain_rate: Optional[float]
    heavy_sessions: tuple[HeavyUsageResult, ...]


class HeavyUsageDetection:
    """Identifies historically heavy battery usage sessions."""

    MINIMUM_SESSIONS = 2

    def __init__(self, access: HistoricalDataAccess):
        self.access = access

    def calculate(self) -> HeavyUsageDetectionResult:
        """Detect unusually high battery drain sessions."""

        sessions = BatteryDischarge(self.access).calculate()

        if len(sessions) < self.MINIMUM_SESSIONS:
            return HeavyUsageDetectionResult(
                session_count=len(sessions),
                average_drain_rate=None,
                heavy_sessions=(),
            )

        average_drain_rate = (
            sum(session.drain_rate for session in sessions)
            / len(sessions)
        )

        heavy_sessions = []

        for session in sessions:
            if session.drain_rate <= average_drain_rate:
                continue

            excess_drain_rate = (
                session.drain_rate - average_drain_rate
            )

            heavy_sessions.append(
                HeavyUsageResult(
                    session=session,
                    drain_rate=session.drain_rate,
                    excess_drain_rate=excess_drain_rate,
                )
            )

        heavy_sessions.sort(
            key=lambda result: result.drain_rate,
            reverse=True,
        )

        return HeavyUsageDetectionResult(
            session_count=len(sessions),
            average_drain_rate=average_drain_rate,
            heavy_sessions=tuple(heavy_sessions),
        )