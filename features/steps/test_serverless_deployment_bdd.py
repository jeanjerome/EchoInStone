import json
from unittest.mock import patch, MagicMock
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from serverless.handler import lambda_handler, kubernetes_handler, http_handler

# Load scenarios from the feature file
scenarios('../serverless_deployment.feature')


class ServerlessTestContext:
    """Context class to hold test state across BDD steps"""
    def __init__(self):
        self.deployment_type = None
        self.response = None
        self.http_app = None
        self.sample_transcriptions = [
            ("Speaker_1", 0.0, 5.0, "Test transcription from BDD")
        ]


@pytest.fixture
def context():
    """Pytest fixture to provide test context"""
    return ServerlessTestContext()


# Lambda deployment steps
@given("I have a Lambda deployment of EchoInStone")
def lambda_deployment(context):
    context.deployment_type = "lambda"


@when(parsers.parse('I send a request with audio URL "{audio_url}"'))
def send_lambda_request(context, audio_url):
    event = {"echo_input": audio_url}
    
    with patch('serverless.handler.EchoInStoneApp') as mock_app_class:
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app
        mock_app.process_audio_sync.return_value = {
            "status": "success",
            "transcriptions": context.sample_transcriptions,
            "message": "Successfully processed"
        }
        
        context.response = lambda_handler(event, None)


@then("I should receive a successful response")
def check_lambda_success(context):
    assert context.response["statusCode"] == 200


@then("the response should contain transcription data")
def check_lambda_transcription_data(context):
    body = json.loads(context.response["body"])
    assert "transcriptions" in body
    assert len(body["transcriptions"]) > 0


@then(parsers.parse("the response should have status code {status_code:d}"))
def check_lambda_status_code(context, status_code):
    assert context.response["statusCode"] == status_code


# Kubernetes deployment steps
@given("I have a Kubernetes deployment of EchoInStone")
def kubernetes_deployment(context):
    context.deployment_type = "kubernetes"


@when(parsers.parse('I send a processing request with audio URL "{audio_url}"'))
def send_kubernetes_request(context, audio_url):
    request_data = {"echo_input": audio_url}
    
    with patch('serverless.handler.EchoInStoneApp') as mock_app_class:
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app
        mock_app.process_audio_sync.return_value = {
            "status": "success",
            "transcriptions": context.sample_transcriptions,
            "message": "Successfully processed"
        }
        
        context.response = kubernetes_handler(request_data)


@then("I should receive a successful processing result")
def check_kubernetes_success(context):
    assert context.response["status"] == "success"


@then("the result should contain speaker transcriptions")
def check_kubernetes_transcriptions(context):
    assert "transcriptions" in context.response
    assert len(context.response["transcriptions"]) > 0


@then(parsers.parse('the result status should be "{status}"'))
def check_kubernetes_status(context, status):
    assert context.response["status"] == status


# HTTP API deployment steps
@given("I have an HTTP API deployment of EchoInStone")
def http_deployment(context):
    context.deployment_type = "http"
    context.http_app = http_handler()


@when(parsers.parse('I POST to "{endpoint}" with audio URL "{audio_url}"'))
def send_http_post_request(context, endpoint, audio_url):
    with patch('serverless.handler.kubernetes_handler') as mock_handler:
        mock_handler.return_value = {
            "status": "success",
            "transcriptions": context.sample_transcriptions
        }
        
        client = context.http_app.test_client()
        context.response = client.post(endpoint, 
                                     json={"echo_input": audio_url},
                                     content_type='application/json')


@then(parsers.parse("I should receive HTTP status code {status_code:d}"))
def check_http_status_code(context, status_code):
    assert context.response.status_code == status_code


@then("the response should contain valid JSON")
def check_http_valid_json(context):
    try:
        json.loads(context.response.data)
    except json.JSONDecodeError:
        pytest.fail("Response does not contain valid JSON")


@then(parsers.parse('the JSON should have status "{status}"'))
def check_http_json_status(context, status):
    data = json.loads(context.response.data)
    assert data["status"] == status


@then("the JSON should contain transcription data")
def check_http_transcription_data(context):
    data = json.loads(context.response.data)
    assert "transcriptions" in data
    assert len(data["transcriptions"]) > 0


# Error handling steps
@given("I have a serverless deployment of EchoInStone")
def generic_serverless_deployment(context):
    context.deployment_type = "serverless"


@when("I send a request without audio URL")
def send_request_without_url(context):
    event = {}  # Missing echo_input
    context.response = lambda_handler(event, None)


@then("I should receive an error response")
def check_error_response(context):
    if context.deployment_type == "serverless":
        assert context.response["statusCode"] != 200
    else:
        assert context.response["status"] == "error"


@then("the error message should indicate missing required parameter")
def check_missing_parameter_error(context):
    if context.deployment_type == "serverless":
        body = json.loads(context.response["body"])
        assert "Missing required parameter" in body["error"]


@when("I send a request with an invalid audio URL")
def send_invalid_url_request(context):
    event = {"echo_input": "invalid_url"}
    
    with patch('serverless.handler.EchoInStoneApp') as mock_app_class:
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app
        mock_app.process_audio_sync.return_value = {
            "status": "error",
            "message": "Processing failed"
        }
        
        context.response = lambda_handler(event, None)


@then("the error status should indicate processing failure")
def check_processing_failure(context):
    if context.deployment_type == "serverless":
        body = json.loads(context.response["body"])
        assert body["status"] == "error"


# Consistency testing steps
@given("I have multiple deployment types of EchoInStone")
def multiple_deployments(context):
    context.deployment_type = "multiple"
    context.responses = {}


@when("I send the same request to each deployment")
def send_to_multiple_deployments(context):
    audio_url = "https://www.youtube.com/watch?v=test"
    
    with patch('serverless.handler.EchoInStoneApp') as mock_app_class:
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app
        mock_app.process_audio_sync.return_value = {
            "status": "success",
            "transcriptions": context.sample_transcriptions
        }
        
        # Lambda response
        lambda_response = lambda_handler({"echo_input": audio_url}, None)
        context.responses["lambda"] = json.loads(lambda_response["body"])
        
        # Kubernetes response
        k8s_response = kubernetes_handler({"echo_input": audio_url})
        context.responses["kubernetes"] = k8s_response


@then("all responses should have consistent format")
def check_consistent_format(context):
    responses = list(context.responses.values())
    assert len(responses) >= 2
    
    # Check all responses have status field
    for response in responses:
        assert "status" in response


@then("all responses should contain the same data structure")
def check_consistent_data_structure(context):
    responses = list(context.responses.values())
    assert len(responses) >= 2
    
    # Check all successful responses have transcriptions
    for response in responses:
        if response["status"] == "success":
            assert "transcriptions" in response


# Health check steps
@when(parsers.parse('I GET "{endpoint}"'))
def send_http_get_request(context, endpoint):
    client = context.http_app.test_client()
    context.response = client.get(endpoint)


@then("the response should indicate service is healthy")
def check_health_response(context):
    data = json.loads(context.response.data)
    assert data["status"] == "healthy"