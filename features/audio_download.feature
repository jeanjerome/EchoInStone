Feature: Audio Download Functionality
  As a user
  I want to download audio files from URLs
  So that I can process remote audio content

  Scenario: Download audio from direct MP3 URL
    Given I have a direct MP3 URL
    When I download the audio file
    Then the file should be downloaded successfully
    And the file should be converted to WAV format

  Scenario: Download audio from URL with authentication headers
    Given I have an MP3 URL that requires specific headers
    When I download the audio file with proper headers
    Then the download should succeed with correct User-Agent
    And the file should be saved in the output directory

  Scenario: Handle network error during download
    Given I have an MP3 URL that is unreachable
    When I attempt to download the audio file
    Then the download should fail gracefully
    And an appropriate error should be logged

  Scenario: Download local audio file
    Given I have a local audio file path
    When I copy the local audio file
    Then the file should be copied successfully
    And the file should be converted to WAV format

  Scenario: Validate accessible URL
    Given I have a valid audio URL
    When I validate the URL
    Then the validation should pass

  Scenario: Validate inaccessible URL
    Given I have an invalid audio URL
    When I validate the URL
    Then the validation should fail