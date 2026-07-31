from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
import torch
import logging
from .diarizer_interface import DiarizerInterface

logger = logging.getLogger(__name__)

class PyannoteDiarizer(DiarizerInterface):
    def __init__(self):
        """Initialize the PyannoteDiarizer with the pretrained model.

        Loads the speaker diarization model and sets up the device for computation.
        """
        try:
            # No credential is passed: huggingface_hub resolves one itself, from
            # the HF_TOKEN environment variable or the login stored by
            # `huggingface-cli login`. Carrying a token in the source tree would
            # leave a secret one commit away from being published.
            self.pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")
            # Move the pipeline to GPU (if available)
            device = torch.device("mps" if torch.backends.mps.is_available() else "cuda" if torch.cuda.is_available() else "cpu")
            self.pipeline.to(device)
            logger.info(f"Diarization pipeline loaded and set to use {device}.")
        except Exception as e:
            # The model is gated, so a missing or unaccepted credential is the
            # likeliest cause. The underlying error names neither remedy.
            logger.error(
                f"Error loading the diarization model: {e}. "
                "Authenticate with `huggingface-cli login` or set HF_TOKEN in the "
                "environment, and accept the model conditions on its Hugging Face page."
            )
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
                output = self.pipeline(audio_path, hook=hook)
                logger.info(f"Diarization successful for file: {audio_path}")
                # The pipeline returns a container holding two annotations. The
                # exclusive one has overlapping speech turns removed, so exactly
                # one speaker is active at any instant. Alignment attributes a
                # single speaker to each transcript segment, so overlap-free
                # turns are what it needs; the caller receives the Annotation
                # itself rather than the container.
                return output.exclusive_speaker_diarization
        except Exception as e:
            logger.error(f"Error during diarization: {e}")
            return None
