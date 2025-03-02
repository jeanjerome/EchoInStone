from pytubefix import YouTube
import logging
from EchoInStone.capture import DownloaderInterface
from EchoInStone.utils.audio_utils import AudioUtils

logger = logging.getLogger(__name__)

class YouTubeDownloader(DownloaderInterface):
    def __init__(self, output_dir='data/videos'):
        """
        Initializes the YouTubeDownloader with a specified output directory.

        Args:
            output_dir (str): The directory where downloaded files will be saved.
        """
        self.output_dir = output_dir

    def download(self, url: str) -> str:
        """
        Downloads audio from a YouTube URL and converts it to WAV format.

        Args:
            url (str): YouTube URL to download audio from.

        Returns:
            str: Path to the saved WAV file if the download and conversion were successful, None otherwise.
        """
        try:
            yt = YouTube(url)
            # Select the audio stream with the highest bitrate
            video_stream = yt.streams.filter(only_audio=True).order_by("abr").desc().first()

            # Download the audio file
            audio_file = video_stream.download(output_path=self.output_dir)

            # Clean up the file name using AudioUtils
            cleaned_file = AudioUtils.clean_filename(audio_file, "mp3")

            # Convert to WAV using AudioUtils
            #wav_file = AudioUtils.convert_to_wav(cleaned_file)
            wav_file = AudioUtils.convert_to_wav_filtered(cleaned_file)
            

            logger.info(f"Audio downloaded and converted to {wav_file}")
            return wav_file
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
            YouTube(url)
            return True
        except Exception:
            logger.warning(f"Invalid YouTube URL: {url}")
            return False
