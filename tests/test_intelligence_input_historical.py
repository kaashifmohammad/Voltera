from orchestration.intelligence_input import IntelligenceInput


def test_historical_defaults_to_empty_dictionary():
    intelligence = IntelligenceInput()

    assert intelligence.historical == {}


def test_historical_data_can_be_supplied():
    historical = {
        "observation_count": 100,
        "average_battery": 62.5,
        "battery_trend": "DECLINING",
    }

    intelligence = IntelligenceInput(
        historical=historical
    )

    assert intelligence.historical == historical


def test_to_dict_includes_historical_data():
    historical = {
        "observation_count": 100,
        "average_battery": 62.5,
    }

    intelligence = IntelligenceInput(
        historical=historical
    )

    result = intelligence.to_dict()

    assert result["historical"] == historical


def test_is_empty_when_all_intelligence_is_empty():
    intelligence = IntelligenceInput()

    assert intelligence.is_empty() is True


def test_is_empty_is_false_when_only_historical_data_exists():
    intelligence = IntelligenceInput(
        historical={
            "observation_count": 10,
        }
    )

    assert intelligence.is_empty() is False


def test_existing_intelligence_fields_remain_supported():
    intelligence = IntelligenceInput(
        context={"risk": "High"},
        learning={"alignment": "Aligned"},
        prediction={"confidence": "High"},
        adaptive={"strength": "High"},
        historical={"observation_count": 50},
    )

    result = intelligence.to_dict()

    assert result["context"] == {"risk": "High"}
    assert result["learning"] == {"alignment": "Aligned"}
    assert result["prediction"] == {"confidence": "High"}
    assert result["adaptive"] == {"strength": "High"}
    assert result["historical"] == {"observation_count": 50}