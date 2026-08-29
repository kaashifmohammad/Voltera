from validation.validation_report import ValidationReport


def test_empty_report_is_not_passed():
    report = ValidationReport()

    assert report.passed is False
    assert report.completed is False
    assert report.failed_stages == []


def test_report_tracks_stage_results():
    report = ValidationReport()

    report.add_stage(
        "build_validation",
        True,
        "Build passed.",
        {"checks": 5},
    )
    report.add_stage(
        "stress_tests",
        False,
        "Stress failure.",
    )

    assert report.passed is False
    assert report.failed_stages == ["stress_tests"]

    data = report.to_dict()

    assert data["total_stages"] == 2
    assert data["passed_stages"] == 1
    assert data["stages"][0]["metrics"]["checks"] == 5


def test_completed_report_has_timestamp():
    report = ValidationReport()

    report.add_stage("build_validation", True)
    report.complete()

    assert report.completed is True
    assert report.to_dict()["completed_at"] is not None


def test_successful_report_summary():
    report = ValidationReport()

    report.add_stage("build_validation", True)
    report.add_stage("reliability_tests", True)
    report.complete()

    assert report.passed is True
    assert "RELEASE READY" in report.summary()