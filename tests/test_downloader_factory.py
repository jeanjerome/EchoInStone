import pytest
import tempfile
import os
from EchoInStone.capture.downloader_factory import get_downloader
from EchoInStone.capture.youtube_downloader import YouTubeDownloader
from EchoInStone.capture.podcast_downloader import PodcastDownloader
from EchoInStone.capture.audio_downloader import AudioDownloader


class TestDownloaderFactory:
    
    def setup_method(self):
        """Setup test environment before each test"""
        self.temp_dir = tempfile.mkdtemp()
    
    def test_youtube_url_returns_youtube_downloader(self):
        """Test that YouTube URLs return YouTubeDownloader"""
        youtube_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s"
        ]
        
        for url in youtube_urls:
            downloader = get_downloader(url, self.temp_dir)
            assert isinstance(downloader, YouTubeDownloader)
    
    def test_podcast_url_returns_podcast_downloader(self):
        """Test that podcast XML URLs return PodcastDownloader"""
        podcast_urls = [
            "https://feeds.npr.org/510289/podcast.xml",
            "https://example.com/podcast.xml",
            "http://feeds.feedburner.com/example.xml"
        ]
        
        for url in podcast_urls:
            downloader = get_downloader(url, self.temp_dir)
            assert isinstance(downloader, PodcastDownloader)
    
    def test_audio_file_url_returns_audio_downloader(self):
        """Test that direct audio file URLs return AudioDownloader"""
        audio_urls = [
            "https://example.com/audio.mp3",
            "https://example.com/audio.wav", 
            "https://example.com/audio.m4a",
            "https://example.com/audio.flac",
            "https://aod-rfi.akamaized.net/rfi/francais/audio/modules/actu/202505/RADIO_FOOT_30-05-25_-_PSG_Reims.mp3"
        ]
        
        for url in audio_urls:
            downloader = get_downloader(url, self.temp_dir)
            assert isinstance(downloader, AudioDownloader)
    
    def test_local_file_path_returns_audio_downloader(self):
        """Test that local file paths return AudioDownloader"""
        # Create a temporary test file
        test_file = os.path.join(self.temp_dir, "test.mp3")
        with open(test_file, 'w') as f:
            f.write('test')
        
        downloader = get_downloader(test_file, self.temp_dir)
        assert isinstance(downloader, AudioDownloader)
    
    def test_generic_url_returns_audio_downloader(self):
        """Test that generic URLs (not YouTube or XML) return AudioDownloader"""
        generic_urls = [
            "https://example.com/some-audio-file",
            "http://radio.example.com/live-stream",
            "https://media.example.com/content"
        ]
        
        for url in generic_urls:
            downloader = get_downloader(url, self.temp_dir)
            assert isinstance(downloader, AudioDownloader)
    
    def test_unsupported_format_raises_error(self):
        """Test that unsupported formats raise ValueError"""
        # Only test cases that should actually raise errors
        # Note: The factory now handles generic URLs with AudioDownloader
        unsupported_urls = [
            "not-a-url-and-not-a-file",
            "completely/invalid/format"
        ]
        
        for url in unsupported_urls:
            with pytest.raises(ValueError, match="Unsupported URL format"):
                get_downloader(url, self.temp_dir)
    
    def test_downloader_output_dir_is_set_correctly(self):
        """Test that the output directory is correctly passed to downloaders"""
        test_url = "https://example.com/test.mp3"
        expected_output_dir = "/custom/output/dir"
        
        downloader = get_downloader(test_url, expected_output_dir)
        assert downloader.output_dir == expected_output_dir