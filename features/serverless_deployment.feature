Feature: Serverless Deployment
  As a developer
  I want to deploy EchoInStone in serverless environments
  So that I can process audio at scale with different deployment strategies

  Scenario: Process audio via AWS Lambda
    Given I have a Lambda deployment of EchoInStone
    When I send a request with audio URL "https://www.youtube.com/watch?v=test"
    Then I should receive a successful response
    And the response should contain transcription data
    And the response should have status code 200

  Scenario: Process audio via Kubernetes Pod
    Given I have a Kubernetes deployment of EchoInStone
    When I send a processing request with audio URL "https://www.youtube.com/watch?v=test"
    Then I should receive a successful processing result
    And the result should contain speaker transcriptions
    And the result status should be "success"

  Scenario: Process audio via HTTP API
    Given I have an HTTP API deployment of EchoInStone
    When I POST to "/process" with audio URL "https://www.youtube.com/watch?v=test"
    Then I should receive HTTP status code 200
    And the response should contain valid JSON
    And the JSON should have status "success"
    And the JSON should contain transcription data

  Scenario: Handle missing input in serverless environment
    Given I have a serverless deployment of EchoInStone
    When I send a request without audio URL
    Then I should receive an error response
    And the error message should indicate missing required parameter

  Scenario: Handle processing failure in serverless environment
    Given I have a serverless deployment of EchoInStone
    When I send a request with an invalid audio URL
    Then I should receive an error response
    And the error status should indicate processing failure

  Scenario: Validate response format consistency across deployments
    Given I have multiple deployment types of EchoInStone
    When I send the same request to each deployment
    Then all responses should have consistent format
    And all responses should contain the same data structure

  Scenario: Health check endpoint for HTTP deployment
    Given I have an HTTP API deployment of EchoInStone
    When I GET "/health"
    Then I should receive HTTP status code 200
    And the response should indicate service is healthy