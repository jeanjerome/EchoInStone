import os
import re
import logging

import feedparser
import requests
from pydub import AudioSegment

from ..capture import DownloaderInterface

logger = logging.getLogger(__name__)


class PodcastDownloader(DownloaderInterface):
    def __init__(self, output_dir: str = "data/podcasts") -> None:
        """Initialize the PodcastDownloader.

        Args:
            output_dir: Directory where downloaded podcast episodes will be saved.
        """
        self.output_dir = output_dir

    @staticmethod
    def _safe_title(title: str) -> str:
        """Strip unicode whitespace and unsafe filesystem chars from a title."""
        collapsed = re.sub(r"\s+", "_", title)
        cleaned = re.sub(r"[^\w-]", "", collapsed)
        return cleaned or "episode"

    def download(self, url: str) -> str | None:
        """Download the first enclosure of a podcast RSS feed and convert to WAV.

        Podcast hosts frequently serve M4A/AAC behind a `.mp3` URL, so the raw
        bytes are decoded via pydub/ffmpeg and re-encoded to WAV — the format
        consumed uniformly by the transcription and diarization pipelines.

        Args:
            url: RSS feed URL containing the podcast episodes.

        Returns:
            Absolute path to the saved WAV file on success, None otherwise.
        """
        try:
            feed = feedparser.parse(url)
            logger.debug(f"Parsed RSS feed with {len(feed.entries)} entries.")
            for entry in feed.entries:
                for link in entry.links:
                    if link.rel != "enclosure":
                        continue

                    audio_url = link.href
                    os.makedirs(self.output_dir, exist_ok=True)

                    safe_title = self._safe_title(entry.title)
                    raw_destination = os.path.join(self.output_dir, f"{safe_title}.audio")
                    wav_destination = os.path.join(self.output_dir, f"{safe_title}.wav")

                    response = requests.get(audio_url, stream=True, timeout=60)
                    response.raise_for_status()
                    with open(raw_destination, "wb") as f:
                        for chunk in response.iter_content(chunk_size=64 * 1024):
                            if chunk:
                                f.write(chunk)

                    audio = AudioSegment.from_file(raw_destination)
                    audio.export(wav_destination, format="wav")
                    try:
                        os.remove(raw_destination)
                    except OSError:
                        pass

                    logger.info(f"Podcast downloaded and converted: {wav_destination}")
                    return os.path.abspath(wav_destination)

            logger.warning("Episode not found.")
            return None
        except Exception as e:
            logger.error(f"Error during download: {e}")
            return None

    def validate_url(self, url: str) -> bool:
        """Validate that a URL parses as a well-formed RSS feed.

        Args:
            url: URL to validate.

        Returns:
            True if the URL parses without errors, False otherwise.
        """
        try:
            feed = feedparser.parse(url)
            if feed.bozo == 0:
                logger.debug(f"Valid RSS feed URL: {url}")
                return True
            logger.warning(f"Invalid RSS feed URL: {url}")
            return False
        except Exception as e:
            logger.error(f"Error validating URL: {e}")
            return False
