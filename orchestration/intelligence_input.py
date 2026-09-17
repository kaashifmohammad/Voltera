from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class IntelligenceInput:
    """
    Unified container for intelligence data entering VOLTERA's
    orchestration layer.

    Each intelligence subsystem contributes its current output
    to one standardized structure.
    """

    context: Dict[str, Any] = field(default_factory=dict)
    learning: Dict[str, Any] = field(default_factory=dict)
    prediction: Dict[str, Any] = field(default_factory=dict)
    adaptive: Dict[str, Any] = field(default_factory=dict)
    historical: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        """
        Convert the unified intelligence input into a dictionary.
        """
        return {
            "context": self.context,
            "learning": self.learning,
            "prediction": self.prediction,
            "adaptive": self.adaptive,
            "historical": self.historical,
        }

    def is_empty(self) -> bool:
        """
        Return True when no intelligence data is available.
        """
        return not any(
            [
                self.context,
                self.learning,
                self.prediction,
                self.adaptive,
                self.historical,
            ]
        )