import os
from urllib.parse import urlparse
from .podcast_downloader import PodcastDownloader
from .youtube_downloader import YouTubeDownloader
from .audio_downloader import AudioDownloader
from .downloader_interface import DownloaderInterface

def get_downloader(url: str, output_dir: str) -> DownloaderInterface:
    """
    Determine the appropriate downloader based on the URL.
    """
    if "youtube.com" in url or "youtu.be" in url:
        return YouTubeDownloader(output_dir=output_dir)
    elif url.endswith(".xml"):
        return PodcastDownloader(output_dir=output_dir)
    elif url.endswith(".mp3") or url.endswith(".wav") or url.endswith(".m4a") or url.endswith(".flac"):
        return AudioDownloader(output_dir=output_dir)
    elif os.path.isfile(url):  # Local file path
        return AudioDownloader(output_dir=output_dir)
    else:
        # Check if it's a valid URL format
        parsed_url = urlparse(url)
        if bool(parsed_url.netloc):
            # It's a URL but doesn't match our specific patterns, try AudioDownloader
            return AudioDownloader(output_dir=output_dir)
        else:
            raise ValueError("Unsupported URL format")