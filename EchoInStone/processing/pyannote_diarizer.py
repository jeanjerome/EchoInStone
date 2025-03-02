from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook
import torch
import logging
import os
from EchoInStone.processing.diarizer_interface import DiarizerInterface
from EchoInStone.utils import timer

# Import HF Token 
try:
    from EchoInStone.config_private import HUGGING_FACE_TOKEN
except ImportError:
    from EchoInStone.config import HUGGING_FACE_TOKEN

logger = logging.getLogger(__name__)

class PyannoteDiarizer(DiarizerInterface):
    def __init__(self, model_name="pyannote/speaker-diarization-3.1", cache_dir=None):
        """Initialize the PyannoteDiarizer with the pretrained model.

        Args:
            model_name (str): Name of the diarization model to use
            cache_dir (str, optional): Directory to cache the model
        """
        self.model_name = model_name
        self.cache_dir = cache_dir or os.path.expanduser("~/.cache/pyannote")
        self.pipeline = None
        self._initialize_pipeline()
    
    def _initialize_pipeline(self):
        """Initialize the diarization pipeline with proper error handling."""
        try:
            # Create cache directory if it doesn't exist
            os.makedirs(self.cache_dir, exist_ok=True)
            
            # Load the pipeline
            self.pipeline = Pipeline.from_pretrained(
                self.model_name,
                use_auth_token=HUGGING_FACE_TOKEN,
                cache_dir=self.cache_dir
            )
            
            # Determine best device
            if torch.backends.mps.is_available():
                device = torch.device("mps")
            elif torch.cuda.is_available():
                device = torch.device("cuda")
            else:
                device = torch.device("cpu")
                
            # Move pipeline to device
            self.pipeline.to(device)
            logger.info(f"Diarization pipeline loaded and set to use {device}.")
        except Exception as e:
            logger.error(f"Error loading the diarization model: {e}")
            self.pipeline = None
            raise
    
    @timer
    def diarize(self, audio_path: str):
        """Perform speaker diarization.
        
        Args:
            audio_path (str): Path to the audio file to diarize
            
        Returns:
            object: Diarization annotation object compatible with SpeakerAligner
        """
        if self.pipeline is None:
            logger.warning("Diarization model not available, attempting to initialize.")
            self._initialize_pipeline()
            if self.pipeline is None:
                return None
        
        try:
            # Perform diarization with progress tracking
            with ProgressHook() as hook:
                diarization = self.pipeline(audio_path, hook=hook)
                
            # Log speaker statistics
            speakers = set()
            for _, _, speaker in diarization.itertracks(yield_label=True):
                speakers.add(speaker)
                
            logger.info(f"Diarization successful for {audio_path}")
            logger.info(f"{len(speakers)} speakers detected")
            return diarization
            
        except Exception as e:
            logger.error(f"Error during diarization: {e}")
            return None
