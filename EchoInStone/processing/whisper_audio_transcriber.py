import torch
import logging
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from EchoInStone.processing.audio_transcriber_interface import AudioTranscriberInterface
from EchoInStone.utils import timer

logger = logging.getLogger(__name__)

class WhisperAudioTranscriber(AudioTranscriberInterface):
    def __init__(self, model_name="openai/whisper-large-v3-turbo"):
        """Initialize the WhisperAudioTranscriber with the specified model.

        Args:
            model_name (str): The name of the model to use for transcription.
        """
        # Configure the device for computation
        if torch.cuda.is_available():
            self.device = "cuda:0"
            self.torch_dtype = torch.float16
        elif torch.backends.mps.is_available():
            self.device = "mps"
            self.torch_dtype = torch.float16
        else:
            self.device = "cpu"
            self.torch_dtype = torch.float32

        logger.info(f"Using device: {self.device} with dtype: {self.torch_dtype}")

        # Load the model and processor
        try:
            self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_name,
                torch_dtype=self.torch_dtype,
                low_cpu_mem_usage=True,
                use_safetensors=True,
            )
            self.model.to(self.device)

            self.processor = AutoProcessor.from_pretrained(model_name)

            # Configure the pipeline for automatic speech recognition
            self.pipe = pipeline(
                "automatic-speech-recognition",
                model=self.model,
                tokenizer=self.processor.tokenizer,
                feature_extractor=self.processor.feature_extractor,
                torch_dtype=self.torch_dtype,
                device=self.device,
                model_kwargs={"attn_implementation": "sdpa"},
                return_timestamps=True,  # or "word"
                #batch_size=24,
                generate_kwargs={
                    "max_new_tokens": 400,
                    "num_beams": 5
                },
                chunk_length_s=5,
                stride_length_s=(1, 1),
            )
            logger.info("Transcription model and pipeline loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading the transcription model: {e}")
            raise

    @timer
    def transcribe(self, audio_path: str) -> tuple:
        """Transcribe audio from the given file path.

        Args:
            audio_path (str): Path to the audio file to transcribe.

        Returns:
            tuple: A tuple containing the transcription text and timestamps.
        """
        try:
            # Perform transcription with timestamps
            result = self.pipe(audio_path)
            transcription = result['text']
            timestamps = result['chunks']
            logger.info(f"Successfully transcribed: {audio_path}")
            return transcription, timestamps
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            return None, None
