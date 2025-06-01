import logging
from typing import List, Tuple, Optional

from .capture.downloader_factory import get_downloader
from .processing import AudioProcessingOrchestrator, WhisperAudioTranscriber, PyannoteDiarizer, SpeakerAligner
from .utils import DataSaver
from .utils import timer, log_time

logger = logging.getLogger(__name__)


class EchoInStoneApp:
    """
    Main application class for EchoInStone audio processing.
    Can be used in both CLI and serverless environments.
    """
    
    def __init__(self, output_dir: str = "results"):
        """
        Initialize the EchoInStone application.
        
        Args:
            output_dir (str): Directory to save output files
        """
        self.output_dir = output_dir
        self._transcriber = None
        self._diarizer = None
        self._aligner = None
        self._data_saver = None
        
    def _initialize_components(self):
        """Lazy initialization of processing components."""
        if self._transcriber is None:
            self._transcriber = WhisperAudioTranscriber()
        if self._diarizer is None:
            self._diarizer = PyannoteDiarizer()
        if self._aligner is None:
            self._aligner = SpeakerAligner()
        if self._data_saver is None:
            self._data_saver = DataSaver(output_dir=self.output_dir)
    
    @timer
    def process_audio(self, echo_input: str, transcription_output: str = "speaker_transcriptions.json") -> Optional[List[Tuple]]:
        """
        Process audio input through the complete pipeline.
        
        Args:
            echo_input (str): URL or path of the audio input
            transcription_output (str): Filename for the transcription output
            
        Returns:
            Optional[List[Tuple]]: List of speaker transcriptions or None if processing failed
        """
        logger.info("Starting transcription process...")
        
        # Initialize components
        self._initialize_components()
        
        # Get appropriate downloader
        downloader = get_downloader(echo_input, self.output_dir)
        
        # Create orchestrator
        orchestrator = AudioProcessingOrchestrator(
            downloader, 
            self._transcriber, 
            self._diarizer, 
            self._aligner, 
            self._data_saver
        )
        
        # Process the input
        speaker_transcriptions = orchestrator.extract_and_transcribe(echo_input)
        
        if speaker_transcriptions:
            # Save the results
            self._data_saver.save_data(transcription_output, speaker_transcriptions)
            logger.info(f"Transcriptions have been saved to {transcription_output}")
            
            # Log results
            for speaker, start_time, end_time, segment_text in speaker_transcriptions:
                logger.info(f"Speaker {speaker} ({start_time:.2f}s to {end_time:.2f}s): {segment_text}")
                
            return speaker_transcriptions
        else:
            logger.warning("No transcriptions were generated.")
            return None
    
    def process_audio_sync(self, echo_input: str) -> dict:
        """
        Synchronous processing method for serverless environments.
        
        Args:
            echo_input (str): URL or path of the audio input
            
        Returns:
            dict: Processing result with status and data
        """
        try:
            transcription_output = "speaker_transcriptions.json"
            speaker_transcriptions = self.process_audio(echo_input, transcription_output)
            
            if speaker_transcriptions:
                return {
                    "status": "success",
                    "transcriptions": speaker_transcriptions,
                    "output_file": transcription_output,
                    "message": f"Successfully processed audio with {len(speaker_transcriptions)} segments"
                }
            else:
                return {
                    "status": "error", 
                    "message": "No transcriptions were generated"
                }
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
            return {
                "status": "error",
                "message": f"Processing failed: {str(e)}"
            }