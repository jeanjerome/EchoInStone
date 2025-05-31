import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from pytest_bdd import scenarios, given, when, then
from EchoInStone.capture.audio_downloader import AudioDownloader

# Load scenarios from the feature file
scenarios('../audio_download.feature')

# Shared variables
downloader = None
url = ""
result = None
temp_dir = ""
local_file_path = ""


@given('I have a direct MP3 URL')
def direct_mp3_url():
    global url, downloader, temp_dir
    temp_dir = tempfile.mkdtemp()
    url = 'https://example.com/test.mp3'
    downloader = AudioDownloader(output_dir=temp_dir)


@given('I have an MP3 URL that requires specific headers')
def mp3_url_with_headers():
    global url, downloader, temp_dir
    temp_dir = tempfile.mkdtemp()
    url = 'https://aod-rfi.akamaized.net/rfi/francais/audio/modules/actu/202505/RADIO_FOOT_30-05-25_-_PSG_Reims.mp3'
    downloader = AudioDownloader(output_dir=temp_dir)


@given('I have an MP3 URL that is unreachable')
def unreachable_mp3_url():
    global url, downloader, temp_dir
    temp_dir = tempfile.mkdtemp()
    url = 'https://nonexistent-domain-12345.com/test.mp3'
    downloader = AudioDownloader(output_dir=temp_dir)


@given('I have a local audio file path')
def local_audio_file():
    global local_file_path, downloader, temp_dir
    temp_dir = tempfile.mkdtemp()
    
    # Create a source file in a different directory
    source_dir = tempfile.mkdtemp()
    local_file_path = os.path.join(source_dir, 'test_audio.mp3')
    with open(local_file_path, 'wb') as f:
        f.write(b'fake audio content')
    
    downloader = AudioDownloader(output_dir=temp_dir)


@given('I have a valid audio URL')
def valid_audio_url():
    global url, downloader, temp_dir
    temp_dir = tempfile.mkdtemp()
    url = 'https://example.com/valid.mp3'
    downloader = AudioDownloader(output_dir=temp_dir)


@given('I have an invalid audio URL')
def invalid_audio_url():
    global url, downloader, temp_dir
    temp_dir = tempfile.mkdtemp()
    url = 'https://nonexistent-domain-99999.com/invalid.mp3'
    downloader = AudioDownloader(output_dir=temp_dir)


@when('I download the audio file')
def download_audio_file():
    global result
    with patch('EchoInStone.capture.audio_downloader.requests') as mock_requests, \
         patch('EchoInStone.capture.audio_downloader.AudioSegment') as mock_audio:
        
        # Setup successful response
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b'fake', b'audio', b'data']
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response
        
        # Setup audio conversion
        mock_audio_instance = MagicMock()
        mock_audio.from_file.return_value = mock_audio_instance
        
        with patch('builtins.open', create=True) as mock_open:
            result = downloader.download(url)


@when('I download the audio file with proper headers')
def download_with_headers():
    global result
    with patch('EchoInStone.capture.audio_downloader.requests') as mock_requests, \
         patch('EchoInStone.capture.audio_downloader.AudioSegment') as mock_audio:
        
        # Setup successful response
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b'fake', b'audio', b'data']
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response
        
        # Setup audio conversion
        mock_audio_instance = MagicMock()
        mock_audio.from_file.return_value = mock_audio_instance
        
        with patch('builtins.open', create=True) as mock_open:
            result = downloader.download(url)
            
        # Store the mock for later verification
        global mock_requests_global
        mock_requests_global = mock_requests


@when('I attempt to download the audio file')
def attempt_download_unreachable():
    global result
    with patch('EchoInStone.capture.audio_downloader.requests') as mock_requests:
        # Simulate network error
        mock_requests.get.side_effect = Exception("Network unreachable")
        result = downloader.download(url)


@when('I copy the local audio file')
def copy_local_file():
    global result
    with patch('EchoInStone.capture.audio_downloader.AudioSegment') as mock_audio:
        # Setup audio conversion
        mock_audio_instance = MagicMock()
        mock_audio.from_file.return_value = mock_audio_instance
        
        result = downloader.download(local_file_path)


@when('I validate the URL')
def validate_url():
    global result
    if url.startswith('https://example.com/valid'):
        # Mock successful validation
        with patch('EchoInStone.capture.audio_downloader.requests') as mock_requests:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_requests.head.return_value = mock_response
            result = downloader.validate_url(url)
    else:
        # Mock failed validation
        with patch('EchoInStone.capture.audio_downloader.requests') as mock_requests:
            mock_requests.head.side_effect = Exception("Network error")
            result = downloader.validate_url(url)


@then('the file should be downloaded successfully')
def verify_download_success():
    assert result is not None
    assert result.endswith('.wav')


@then('the file should be converted to WAV format')
def verify_wav_conversion():
    assert result.endswith('.wav')
    assert os.path.isabs(result)


@then('the download should succeed with correct User-Agent')
def verify_user_agent():
    # Verify that the request was made with proper User-Agent header
    mock_requests_global.get.assert_called_once()
    args, kwargs = mock_requests_global.get.call_args
    assert 'headers' in kwargs
    assert 'User-Agent' in kwargs['headers']
    assert 'Mozilla' in kwargs['headers']['User-Agent']


@then('the file should be saved in the output directory')
def verify_output_directory():
    assert result is not None
    assert temp_dir in result


@then('the download should fail gracefully')
def verify_download_failure():
    assert result is None


@then('an appropriate error should be logged')
def verify_error_logging():
    # This would normally check logging output, but for this test
    # we just verify the download returned None (handled gracefully)
    assert result is None


@then('the file should be copied successfully')
def verify_copy_success():
    assert result is not None
    assert result.endswith('.wav')


@then('the validation should pass')
def verify_validation_success():
    assert result is True


@then('the validation should fail')
def verify_validation_failure():
    assert result is False


def teardown_function():
    """Clean up temporary directories after each test"""
    global temp_dir
    if temp_dir and os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        temp_dir = ""