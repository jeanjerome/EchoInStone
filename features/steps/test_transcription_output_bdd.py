from pytest_bdd import scenarios, given, when, then
from EchoInStone.processing import WhisperAudioTranscriber

# Load scenarios from the .feature file
# This function loads BDD scenarios defined in the specified feature file for testing transcription output.
scenarios('../transcription_output.feature')

# Shared variables
# Global variables to store the path of the downloaded audio file and the transcription output.
downloaded_file_path = ""
transcription_output = ""
transcriber = WhisperAudioTranscriber()

@given('the audio file is transcribed')
def setup_transcription():
    global downloaded_file_path
    # Ensure the audio file has been downloaded in a previous step.
    # Set the path to the audio file to be transcribed.
    downloaded_file_path = 'tests/resources/sample_speech.wav'

@when('the transcription is generated')
def generate_transcription():
    global transcription_output, downloaded_file_path, transcriber
    # Generate the transcription from the audio file using the transcriber.
    transcription_output = transcriber.transcribe(downloaded_file_path)

@then('the output should be valid')
def check_transcription_output():
    # Verify that the transcription output is valid and contains the expected text.
    assert transcription_output is not None, "Transcription output should not be None"
    text = transcription_output[0]
    # Check the beginning of the countdown (stable across transformers versions)
    assert '10, 9, 8, 7' in text, f"Transcription should contain the start of the countdown, got: {text}"
    # Verify that key numbers from the countdown are present
    for num in ['10', '9', '8', '7', '3', '2', '1']:
        assert num in text, f"Transcription should contain '{num}', got: {text}"
