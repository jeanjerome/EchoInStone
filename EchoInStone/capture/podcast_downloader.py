import feedparser
import requests
import logging
from EchoInStone.capture import DownloaderInterface
import re

logger = logging.getLogger(__name__)

class PodcastDownloader(DownloaderInterface):
    def __init__(self, output_dir='data/podcasts'):
        """
        Initializes the PodcastDownloader with a specified output directory.

        Args:
            output_dir (str): The directory where downloaded podcast episodes will be saved.
        """
        self.output_dir = output_dir

    def download(self, url: str) -> bool:
        """
        Downloads a podcast episode from an RSS feed URL.

        Args:
            url (str): RSS feed URL containing the podcast episodes.

        Returns:
            bool: True if the download was successful, False otherwise.
        """
        try:
            feed = feedparser.parse(url)
            logger.debug(f"Parsed RSS feed with {len(feed.entries)} entries.")
            for entry in feed.entries:
                for link in entry.links:
                    if link.rel == 'enclosure':
                        audio_url = link.href
                        response = requests.get(audio_url)
                        audio_file = f"{self.output_dir}/{entry.title}.mp3"
                        safe_audio_file = re.sub(r'[^\w\s-]', '', audio_file).replace(' ', '_')
                        with open(safe_audio_file, 'wb') as f:
                            f.write(response.content)
                        logger.info(f"Podcast downloaded: {safe_audio_file}")
                        return True
            logger.warning("Episode not found.")
            return False
        except Exception as e:
            logger.error(f"Error during download: {e}")
            return False

    def validate_url(self, url: str) -> bool:
        """
        Validates if a URL is a valid RSS feed URL for podcasts.

        Args:
            url (str): URL to validate.

        Returns:
            bool: True if the URL is a valid RSS feed URL, False otherwise.
        """
        try:
            feed = feedparser.parse(url)
            if feed.bozo == 0:  # 0 indicates no error in parsing
                logger.debug(f"Valid RSS feed URL: {url}")
                return True
            logger.warning(f"Invalid RSS feed URL: {url}")
            return False
        except Exception as e:
            logger.error(f"Error validating URL: {e}")
            return False
