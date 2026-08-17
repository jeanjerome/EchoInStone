import os
import re
import logging
from yt_dlp import YoutubeDL
from ..capture import DownloaderInterface

logger = logging.getLogger(__name__)

class YouTubeDownloader(DownloaderInterface):
    def __init__(self, output_dir='data/videos'):
        """
        Initializes the YouTubeDownloader with a specified output directory.

        Args:
            output_dir (str): The directory where downloaded files will be saved.
        """
        self.output_dir = output_dir

    def _ydl_options(self) -> dict:
        """
        Builds the extractor options shared by download and validation.

        YouTube signs its stream URLs with obfuscated JavaScript, so extraction
        needs a JS runtime to reach the full set of formats. Every runtime
        yt-dlp supports is enabled and the first one installed is used;
        without any of them the extractor falls back to clients whose streams
        YouTube answers with HTTP 403.

        Returns:
            dict: Options passed to YoutubeDL.
        """
        return {
            'noplaylist': True,
            'quiet': True,
            'no_warnings': True,
            'logger': logger,
            'js_runtimes': {'deno': {}, 'node': {}, 'bun': {}, 'quickjs': {}},
        }

    def download(self, url: str) -> str:
        """
        Downloads audio from a YouTube URL and converts it to WAV format.

        Args:
            url (str): YouTube URL to download audio from.

        Returns:
            str: Path to the saved WAV file if the download and conversion were successful, None otherwise.
        """
        try:
            os.makedirs(self.output_dir, exist_ok=True)

            options = {
                **self._ydl_options(),
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(self.output_dir, '%(id)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'wav',
                }],
            }

            with YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)

            downloaded_file = info['requested_downloads'][0]['filepath']

            # Clean up the file name
            dir_path = os.path.dirname(downloaded_file)
            safe_base = re.sub(r'[^\w\s-]', '', info['title']).replace(' ', '_')
            wav_file = os.path.join(dir_path, safe_base + '.wav')
            os.replace(downloaded_file, wav_file)

            logger.info(f"Audio downloaded and converted to {wav_file}")
            return os.path.abspath(wav_file)
        except Exception as e:
            logger.error(f"Error during download: {e}")
            return None

    def validate_url(self, url: str) -> bool:
        """
        Validates if a URL is a valid YouTube URL.

        Args:
            url (str): URL to validate.

        Returns:
            bool: True if the URL is a valid YouTube URL, False otherwise.
        """
        try:
            with YoutubeDL(self._ydl_options()) as ydl:
                ydl.extract_info(url, download=False)
            return True
        except Exception:
            logger.warning(f"Invalid YouTube URL: {url}")
            return False
