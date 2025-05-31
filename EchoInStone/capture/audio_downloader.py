import os
import shutil
import logging
import requests
from urllib.parse import urlparse
from pydub import AudioSegment
from . import DownloaderInterface

logger = logging.getLogger(__name__)

class AudioDownloader(DownloaderInterface):
    def __init__(self, output_dir='data/files'):
        """
        Initializes the AudioDownloader with a specified output directory.

        Args:
            output_dir (str): The directory where copied files will be saved.
        """
        self.output_dir = output_dir

    def download(self, file_path: str) -> str:
        """
        Downloads an audio file from a URL or copies from a local file path,
        then converts it to WAV format for compatibility with PyAnnote.

        Args:
            file_path (str): URL or local file path to download/copy the file from.

        Returns:
            str: Absolute path to the downloaded and converted WAV file if successful, None otherwise.
        """
        try:
            # Ensure the output directory exists
            os.makedirs(self.output_dir, exist_ok=True)
            logger.debug(f"Output directory created or already exists: {self.output_dir}")

            # Check if it's a URL or local file
            parsed_url = urlparse(file_path)
            is_url = bool(parsed_url.netloc)
            
            if is_url:
                # Download from URL
                logger.info(f"Downloading audio from URL: {file_path}")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(file_path, stream=True, headers=headers)
                response.raise_for_status()
                
                # Get the file name from the URL
                file_name = os.path.basename(parsed_url.path)
                if not file_name:
                    file_name = "downloaded_audio.mp3"
                
                file_base, file_ext = os.path.splitext(file_name)
                destination_path = os.path.join(self.output_dir, file_name)
                
                # Save the downloaded file
                with open(destination_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                logger.info(f"File downloaded to {destination_path}")
            else:
                # Copy from local file
                logger.info(f"Copying local file: {file_path}")
                file_name = os.path.basename(file_path)
                file_base, file_ext = os.path.splitext(file_name)
                destination_path = os.path.join(self.output_dir, file_name)
                
                # Copy the file to the destination path
                shutil.copy2(file_path, destination_path)
                logger.info(f"File copied to {destination_path}")
            
            # Always convert to WAV for PyAnnote compatibility
            audio = AudioSegment.from_file(destination_path)
            wav_file = os.path.join(self.output_dir, f"{file_base}.wav")
            audio.export(wav_file, format="wav")
            logger.info(f"File converted to WAV: {wav_file}")
            
            # Return the absolute path to the WAV file
            return os.path.abspath(wav_file)
        except Exception as e:
            logger.error(f"Error during file download/copy/conversion: {e}")
            return None

    def validate_url(self, file_path: str) -> bool:
        """
        Validates if a file path or URL is valid.

        Args:
            file_path (str): Local file path or URL to validate.

        Returns:
            bool: True if the file path/URL is valid, False otherwise.
        """
        # Check if it's a URL
        parsed_url = urlparse(file_path)
        is_url = bool(parsed_url.netloc)
        
        if is_url:
            # For URLs, just check if the URL format is valid
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.head(file_path, timeout=10, headers=headers)
                if response.status_code == 200:
                    logger.debug(f"URL is valid: {file_path}")
                    return True
                else:
                    logger.warning(f"URL returned status {response.status_code}: {file_path}")
                    return False
            except Exception as e:
                logger.warning(f"Invalid URL: {file_path} - {e}")
                return False
        else:
            # For local files, check if the file exists
            if os.path.isfile(file_path):
                logger.debug(f"File path is valid: {file_path}")
                return True
            else:
                logger.warning(f"Invalid file path: {file_path}")
                return False
