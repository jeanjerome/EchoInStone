import logging
from EchoInStone.capture.downloader_factory import get_downloader
from EchoInStone.processing import AudioProcessingOrchestrator, WhisperAudioTranscriber, PyannoteDiarizer, SpeakerAligner
from EchoInStone.utils import DataSaver

logger = logging.getLogger(__name__)

class EchoInStoneApp:
    def __init__(self, output_dir: str):
        """
        Application logic to manage the entire processing pipeline.
        """
        self.output_dir = output_dir
        self.saver = DataSaver(output_dir=output_dir)

    def run(self, echo_input: str):
        """
        Runs the entire audio processing pipeline.
        """
        logger.info("Initializing processing components...")
        
        # Initialization moved here
        downloader = get_downloader(echo_input, self.output_dir)
        transcriber = WhisperAudioTranscriber()
        diarizer = PyannoteDiarizer()
        aligner = SpeakerAligner()

        orchestrator = AudioProcessingOrchestrator(downloader, transcriber, diarizer, aligner, self.saver)

        logger.info("Starting transcription process...")
        return orchestrator.process(echo_input)

    def save_results(self, output_file: str, transcriptions):
        """
        Handles the saving of results.
        """
        self.saver.save_data(output_file, transcriptions)
        logger.info(f"Transcriptions have been saved to {output_file}")
