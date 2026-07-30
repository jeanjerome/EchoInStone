from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
import torch
import logging
from .diarizer_interface import DiarizerInterface

# Import HF Token 
try:
    from ..config import HUGGING_FACE_TOKEN
except ImportError:
    from ..config_private import HUGGING_FACE_TOKEN

logger = logging.getLogger(__name__)

class PyannoteDiarizer(DiarizerInterface):
    def __init__(self):
        """Initialize the PyannoteDiarizer with the pretrained model.

        Loads the speaker diarization model and sets up the device for computation.
        """
        try:
            self.pipeline = Pipeline.from_pretrained(
                "pyannote/speaker-diarization-3.1",
                token=HUGGING_FACE_TOKEN
            )
            # Move the pipeline to GPU (if available)
            device = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
            self.pipeline.to(device)
            logger.info(f"Diarization pipeline loaded and set to use {device}.")
        except Exception as e:
            logger.error(f"Error loading the diarization model: {e}")
            self.pipeline = None

    def diarize(self, audio_path: str):
        """Perform speaker diarization on the given audio file.

        Args:
            audio_path (str): Path to the audio file to diarize.

        Returns:
            Diarization result or None if diarization fails.
        """
        if self.pipeline is None:
            logger.warning("Diarization model is not available.")
            return None

        try:
            # Perform diarization with progress tracking
            with ProgressHook() as hook:
                diarization = self.pipeline(audio_path, hook=hook)
                logger.info(f"Diarization successful for file: {audio_path}")
                return diarization
        except Exception as e:
            logger.error(f"Error during diarization: {e}")
            return None
