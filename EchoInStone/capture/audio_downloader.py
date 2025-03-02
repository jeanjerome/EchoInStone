import os
import shutil
import logging
from EchoInStone.capture import DownloaderInterface

logger = logging.getLogger(__name__)

class AudioDownloader(DownloaderInterface):
    def __init__(self, output_dir='data/files'):
        """
        Initializes the AudioDownloader with a specified output directory.

        Args:
            output_dir (str): The directory where copied files will be saved.
        """
        self.output_dir = output_dir

    def download(self, file_path: str) -> bool:
        """
        Copies an audio file from a local file path to the specified output path.

        Args:
            file_path (str): Local file path to copy the file from.

        Returns:
            bool: True if the file was successfully copied, False otherwise.
        """
        try:
            # Ensure the output directory exists
            os.makedirs(self.output_dir, exist_ok=True)
            logger.debug(f"Output directory created or already exists: {self.output_dir}")

            # Get the file name from the file path
            file_name = os.path.basename(file_path)
            destination_path = os.path.join(self.output_dir, file_name)

            # Copy the file to the destination path
            shutil.copy2(file_path, destination_path)
            logger.info(f"File copied to {destination_path}")
            return True
        except Exception as e:
            logger.error(f"Error during file copy: {e}")
            return False

    def validate_url(self, file_path: str) -> bool:
        """
        Validates if a file path is valid and the file exists.

        Args:
            file_path (str): Local file path to validate.

        Returns:
            bool: True if the file path is valid and the file exists, False otherwise.
        """
        if os.path.isfile(file_path):
            logger.debug(f"File path is valid: {file_path}")
            return True
        else:
            logger.warning(f"Invalid file path: {file_path}")
            return False
