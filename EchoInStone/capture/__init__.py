# capture/__init__.py

from EchoInStone.capture.downloader_interface import DownloaderInterface
from EchoInStone.capture.youtube_downloader import YouTubeDownloader
from EchoInStone.capture.podcast_downloader import PodcastDownloader
from EchoInStone.capture.audio_downloader import AudioDownloader

__all__ = [
    'DownloaderInterface',
    'YouTubeDownloader',
    'PodcastDownloader',
    'AudioDownloader'
]
