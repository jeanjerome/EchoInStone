import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from EchoInStone.capture.downloader_factory import get_downloader
from EchoInStone.capture.audio_downloader import AudioDownloader


class TestIntegration:
    """Integration tests for the audio download functionality"""
    
    def setup_method(self):
        """Setup test environment before each test"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup test environment after each test"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_rfi_mp3_url_uses_audio_downloader(self):
        """Test that the specific RFI MP3 URL that was failing uses AudioDownloader"""
        rfi_url = "https://aod-rfi.akamaized.net/rfi/francais/audio/modules/actu/202505/RADIO_FOOT_30-05-25_-_PSG_Reims.mp3"
        
        downloader = get_downloader(rfi_url, self.temp_dir)
        assert isinstance(downloader, AudioDownloader)
    
    @patch('EchoInStone.capture.audio_downloader.requests')
    @patch('EchoInStone.capture.audio_downloader.AudioSegment')
    def test_rfi_mp3_url_download_process(self, mock_audio, mock_requests):
        """Test that the RFI MP3 URL follows the correct download process"""
        rfi_url = "https://aod-rfi.akamaized.net/rfi/francais/audio/modules/actu/202505/RADIO_FOOT_30-05-25_-_PSG_Reims.mp3"
        
        # Setup mocks
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b'fake', b'mp3', b'content']
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response
        
        mock_audio_instance = MagicMock()
        mock_audio.from_file.return_value = mock_audio_instance
        
        # Get downloader and test download
        downloader = get_downloader(rfi_url, self.temp_dir)
        
        # Mock file writing
        with patch('builtins.open') as mock_file:
            result = downloader.download(rfi_url)
            
            # Verify URL was requested with proper headers
            mock_requests.get.assert_called_once()
            args, kwargs = mock_requests.get.call_args
            assert args[0] == rfi_url
            assert kwargs['stream'] == True
            assert 'User-Agent' in kwargs['headers']
            
            # Verify the result
            assert result is not None
            assert result.endswith('.wav')
    
    def test_various_mp3_urls_use_audio_downloader(self):
        """Test that various MP3 URLs all use AudioDownloader"""
        mp3_urls = [
            "https://example.com/audio.mp3",
            "https://media.radiofrance-podcast.net/podcast09/test.mp3",
            "https://aod-rfi.akamaized.net/rfi/francais/audio/modules/actu/202505/RADIO_FOOT_30-05-25_-_PSG_Reims.mp3",
            "http://example.com/folder/audio.mp3"
        ]
        
        for url in mp3_urls:
            downloader = get_downloader(url, self.temp_dir)
            assert isinstance(downloader, AudioDownloader), f"Failed for URL: {url}"