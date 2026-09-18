from orchestration.intelligence_input import IntelligenceInput
from orchestration.orchestration_input import OrchestrationInput


def test_historical_property_is_exposed():
    historical = {
        "observation_count": 100,
        "average_battery": 62.5,
        "battery_trend": "DECLINING",
    }

    intelligence = IntelligenceInput(
        historical=historical
    )

    orchestration_input = OrchestrationInput(
        intelligence=intelligence
    )

    assert orchestration_input.historical == historical


def test_to_dict_includes_historical_data():
    historical = {
        "observation_count": 100,
        "average_battery": 62.5,
    }

    intelligence = IntelligenceInput(
        historical=historical
    )

    orchestration_input = OrchestrationInput(
        intelligence=intelligence
    )

    result = orchestration_input.to_dict()

    assert result["historical"] == historical


def test_existing_properties_remain_available():
    intelligence = IntelligenceInput(
        context={"risk": "High"},
        learning={"alignment": "Aligned"},
        prediction={"confidence": "High"},
        adaptive={"strength": "High"},
        historical={"observation_count": 50},
    )

    orchestration_input = OrchestrationInput(
        intelligence=intelligence
    )

    assert orchestration_input.context == {"risk": "High"}
    assert orchestration_input.learning == {"alignment": "Aligned"}
    assert orchestration_input.prediction == {"confidence": "High"}
    assert orchestration_input.adaptive == {"strength": "High"}
    assert orchestration_input.historical == {
        "observation_count": 50
    }


def test_empty_historical_data_is_supported():
    intelligence = IntelligenceInput()

    orchestration_input = OrchestrationInput(
        intelligence=intelligence
    )

    assert orchestration_input.historical == {}