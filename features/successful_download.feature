Feature: Successful Download
  As a user
  I want to download files successfully
  So that I can process them further

  # Downloads a real video. YouTube serves a bot challenge to datacenter
  # addresses, so this cannot pass from a hosted CI runner and is deselected
  # there; it stays meaningful from a workstation.
  @youtube
  Scenario: Successful YouTube download
    Given the URL is a valid YouTube URL
    When the file is downloaded
    Then the download should be successful
