import sys
import os
import json
from unittest.mock import MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

with patch("boto3.client"):
    from notifyEmail import lambda_handler, build_alerts_by_email, send_alert_email


def make_sns_event(payload):
    return {"Records": [{"Sns": {"Message": json.dumps(payload)}}]}


SAMPLE_CVES = {
    "Timmy Blud": [
        {
            "cve_id": "CVE-2024-1234",
            "name": "Critical RCE",
            "date_added": "2024-01-01",
            "due_date": "2024-01-15",
            "cvss_score": 9.8,
            "epss_score": 0.75,
            "description": "Remote code execution vulnerability.",
        }
    ]
}


def test_missing_records_returns_400():
    response = lambda_handler({}, None)
    assert response["statusCode"] == 400
    assert response["body"] == "No SNS records"


def test_empty_records_returns_400():
    response = lambda_handler({"Records": []}, None)
    assert response["statusCode"] == 400


def test_invalid_sns_message_json_returns_400():
    event = {"Records": [{"Sns": {"Message": "not-json"}}]}
    response = lambda_handler(event, None)
    assert response["statusCode"] == 400
    assert response["body"] == "Invalid SNS payload"


def test_no_new_cves_returns_200():
    response = lambda_handler(make_sns_event({"new_cves": {}}), None)
    assert response["statusCode"] == 200
    assert response["body"] == "No CVEs to alert on"


@patch("notifyEmail.build_alerts_by_email")
def test_no_subscribers_returns_200(mock_build):
    mock_build.return_value = {}
    response = lambda_handler(make_sns_event({"new_cves": SAMPLE_CVES}), None)
    assert response["statusCode"] == 200
    assert response["body"] == "No subscribers to alert"


@patch("notifyEmail.send_alert_email")
@patch("notifyEmail.build_alerts_by_email")
def test_sends_emails_to_all_subscribers(mock_build, mock_send):
    mock_build.return_value = {"test@gmail.com": SAMPLE_CVES, "other@gmail.com": SAMPLE_CVES}
    response = lambda_handler(make_sns_event({"new_cves": SAMPLE_CVES}), None)
    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {"sent": 2, "failed": 0}
    assert mock_send.call_count == 2


@patch("notifyEmail.send_alert_email")
@patch("notifyEmail.build_alerts_by_email")
def test_failed_emails_counted(mock_build, mock_send):
    mock_build.return_value = {"test@gmail.com": SAMPLE_CVES, "bad@gmail.com": SAMPLE_CVES}
    mock_send.side_effect = [None, Exception("SES error")]
    response = lambda_handler(make_sns_event({"new_cves": SAMPLE_CVES}), None)
    assert json.loads(response["body"]) == {"sent": 1, "failed": 1}


@patch("notifyEmail.get_db_connection")
def test_groups_cves_by_subscriber_email(mock_conn):
    cur = MagicMock()
    cur.fetchall.return_value = [("test@gmail.com", "Timmy Blud"), ("other@gmail.com", "Timmy Blud")]
    mock_conn.return_value.cursor.return_value = cur

    result = build_alerts_by_email(SAMPLE_CVES)
    assert "test@gmail.com" in result
    assert "other@gmail.com" in result
    assert "Timmy Blud" in result["test@gmail.com"]


@patch("notifyEmail.get_db_connection")
def test_no_subscribers_returns_empty(mock_conn):
    cur = MagicMock()
    cur.fetchall.return_value = []
    mock_conn.return_value.cursor.return_value = cur

    result = build_alerts_by_email(SAMPLE_CVES)
    assert result == {}


@patch("notifyEmail.get_db_connection")
def test_db_exception_raises(mock_conn):
    mock_conn.side_effect = Exception("DB error")
    raised = False
    try:
        build_alerts_by_email(SAMPLE_CVES)
    except Exception:
        raised = True
    assert raised


@patch("notifyEmail.ses")
@patch.dict(os.environ, {"FROM_EMAIL": "noreply@example.com"})
def test_sends_email_via_ses(mock_ses):
    import notifyEmail
    notifyEmail.FROM_EMAIL = "noreply@example.com"
    send_alert_email("test@gmail.com", SAMPLE_CVES)
    mock_ses.send_email.assert_called_once()
    call_kwargs = mock_ses.send_email.call_args[1]
    assert call_kwargs["Destination"]["ToAddresses"] == ["test@gmail.com"]
    assert call_kwargs["Source"] == "noreply@example.com"


@patch("notifyEmail.ses")
def test_subject_includes_cve_count_and_company_count(mock_ses):
    import notifyEmail
    notifyEmail.FROM_EMAIL = "noreply@example.com"
    send_alert_email("test@gmail.com", SAMPLE_CVES)
    subject = mock_ses.send_email.call_args[1]["Message"]["Subject"]["Data"]
    assert "1" in subject


@patch("notifyEmail.ses")
def test_long_description_truncated(mock_ses):
    import notifyEmail
    notifyEmail.FROM_EMAIL = "noreply@example.com"
    long_desc_cves = {
        "Timmy Blud": [{
            "cve_id": "CVE-2024-0001",
            "name": "Test",
            "date_added": "2024-01-01",
            "due_date": "2024-01-15",
            "cvss_score": None,
            "epss_score": None,
            "description": "x" * 400,
        }]
    }
    send_alert_email("test@gmail.com", long_desc_cves)
    body = mock_ses.send_email.call_args[1]["Message"]["Body"]["Text"]["Data"]
    assert "..." in body


@patch("notifyEmail.ses")
def test_email_body_contains_cve_id(mock_ses):
    import notifyEmail
    notifyEmail.FROM_EMAIL = "noreply@example.com"
    send_alert_email("test@gmail.com", SAMPLE_CVES)
    body = mock_ses.send_email.call_args[1]["Message"]["Body"]["Text"]["Data"]
    assert "CVE-2024-1234" in body
    assert "Timmy Blud" in body


@patch("notifyEmail.ses")
def test_optional_scores_omitted_when_none(mock_ses):
    import notifyEmail
    notifyEmail.FROM_EMAIL = "noreply@example.com"
    no_score_cves = {
        "Timmy Blud": [{
            "cve_id": "CVE-2024-9999",
            "name": "Test",
            "date_added": "2024-01-01",
            "due_date": "2024-01-15",
            "cvss_score": None,
            "epss_score": None,
            "description": "",
        }]
    }
    send_alert_email("test@gmail.com", no_score_cves)
    body = mock_ses.send_email.call_args[1]["Message"]["Body"]["Text"]["Data"]
    assert "CVSS:" not in body
    assert "EPSS:" not in body
