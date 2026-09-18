from dataclasses import dataclass
from typing import Any, Dict

from .intelligence_input import IntelligenceInput


@dataclass
class OrchestrationInput:
    """
    Input contract for the VOLTERA orchestrator.

    The orchestration layer receives one unified intelligence
    structure instead of handling separate intelligence payloads.
    """

    intelligence: IntelligenceInput

    def to_dict(self) -> Dict[str, Dict[str, Any]]:
        """
        Convert orchestration input into a serializable dictionary.
        """
        return self.intelligence.to_dict()

    @property
    def context(self) -> Dict[str, Any]:
        return self.intelligence.context

    @property
    def learning(self) -> Dict[str, Any]:
        return self.intelligence.learning

    @property
    def prediction(self) -> Dict[str, Any]:
        return self.intelligence.prediction

    @property
    def adaptive(self) -> Dict[str, Any]:
        return self.intelligence.adaptive

    @property
    def historical(self) -> Dict[str, Any]:
        return self.intelligence.historical