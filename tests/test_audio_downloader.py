import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock, mock_open
from EchoInStone.capture.audio_downloader import AudioDownloader


class TestAudioDownloader:
    
    def setup_method(self):
        """Setup test environment before each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.downloader = AudioDownloader(output_dir=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment after each test"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_local_file_copy_and_conversion(self):
        """Test copying and converting a local audio file"""
        # Create a temporary test file in a different directory to avoid same-file error
        source_dir = tempfile.mkdtemp()
        test_file = os.path.join(source_dir, "test_input.mp3")
        with open(test_file, 'wb') as f:
            f.write(b'fake mp3 content')
        
        try:
            # Mock AudioSegment to avoid actual audio processing
            with patch('EchoInStone.capture.audio_downloader.AudioSegment') as mock_audio:
                mock_audio_instance = MagicMock()
                mock_audio.from_file.return_value = mock_audio_instance
                
                result = self.downloader.download(test_file)
                
                # Verify the file was processed
                assert result is not None
                assert result.endswith('.wav')
                assert os.path.isabs(result)
                
                # Verify AudioSegment was called correctly
                mock_audio.from_file.assert_called_once()
                mock_audio_instance.export.assert_called_once()
        finally:
            # Clean up source directory
            if os.path.exists(source_dir):
                shutil.rmtree(source_dir)
    
    @patch('EchoInStone.capture.audio_downloader.requests')
    @patch('EchoInStone.capture.audio_downloader.AudioSegment')
    def test_url_download_and_conversion(self, mock_audio, mock_requests):
        """Test downloading and converting an audio file from URL"""
        # Setup mocks
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b'fake', b'mp3', b'content']
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response
        
        mock_audio_instance = MagicMock()
        mock_audio.from_file.return_value = mock_audio_instance
        
        test_url = "https://example.com/test.mp3"
        
        # Mock file writing
        with patch('builtins.open', mock_open()) as mock_file:
            result = self.downloader.download(test_url)
            
            # Verify URL was requested with proper headers
            mock_requests.get.assert_called_once()
            args, kwargs = mock_requests.get.call_args
            assert args[0] == test_url
            assert kwargs['stream'] == True
            assert 'User-Agent' in kwargs['headers']
            
            # Verify file was written
            mock_file.assert_called()
            
            # Verify audio conversion
            mock_audio.from_file.assert_called_once()
            mock_audio_instance.export.assert_called_once()
            
            # Verify result
            assert result is not None
            assert result.endswith('.wav')
    
    @patch('EchoInStone.capture.audio_downloader.requests')
    def test_url_download_with_request_error(self, mock_requests):
        """Test handling of HTTP errors during URL download"""
        # Setup mock to raise an exception
        mock_requests.get.side_effect = Exception("Network error")
        
        test_url = "https://example.com/test.mp3"
        result = self.downloader.download(test_url)
        
        # Verify error handling
        assert result is None
    
    def test_validate_url_local_file_exists(self):
        """Test validation of existing local file"""
        # Create a test file
        test_file = os.path.join(self.temp_dir, "test.mp3")
        with open(test_file, 'w') as f:
            f.write('test')
        
        result = self.downloader.validate_url(test_file)
        assert result == True
    
    def test_validate_url_local_file_not_exists(self):
        """Test validation of non-existing local file"""
        test_file = os.path.join(self.temp_dir, "nonexistent.mp3")
        
        result = self.downloader.validate_url(test_file)
        assert result == False
    
    @patch('EchoInStone.capture.audio_downloader.requests')
    def test_validate_url_valid_http_url(self, mock_requests):
        """Test validation of valid HTTP URL"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_requests.head.return_value = mock_response
        
        test_url = "https://example.com/test.mp3"
        result = self.downloader.validate_url(test_url)
        
        # Verify request was made with proper headers
        mock_requests.head.assert_called_once()
        args, kwargs = mock_requests.head.call_args
        assert args[0] == test_url
        assert 'User-Agent' in kwargs['headers']
        assert kwargs['timeout'] == 10
        
        assert result == True
    
    @patch('EchoInStone.capture.audio_downloader.requests')
    def test_validate_url_invalid_http_url(self, mock_requests):
        """Test validation of invalid HTTP URL"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_requests.head.return_value = mock_response
        
        test_url = "https://example.com/nonexistent.mp3"
        result = self.downloader.validate_url(test_url)
        
        assert result == False
    
    @patch('EchoInStone.capture.audio_downloader.requests')
    def test_validate_url_network_error(self, mock_requests):
        """Test validation with network error"""
        mock_requests.head.side_effect = Exception("Network error")
        
        test_url = "https://example.com/test.mp3"
        result = self.downloader.validate_url(test_url)
        
        assert result == False