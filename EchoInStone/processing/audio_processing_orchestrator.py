import logging
from EchoInStone.capture import DownloaderInterface
from EchoInStone.processing.audio_transcriber_interface import AudioTranscriberInterface
from EchoInStone.processing.diarizer_interface import DiarizerInterface
from EchoInStone.processing.aligner_interface import AlignerInterface
from EchoInStone.utils import DataSaver

logger = logging.getLogger(__name__)

class AudioProcessingOrchestrator:
    def __init__(self, downloader: DownloaderInterface,
                       transcriber: AudioTranscriberInterface,
                       diarizer: DiarizerInterface,
                       aligner: AlignerInterface,
                       data_saver: DataSaver):
        """
        Initialize the audio processing orchestrator.

        Args:
            downloader (DownloaderInterface): Handles downloading the audio.
            transcriber (AudioTranscriberInterface): Handles audio transcription.
            diarizer (DiarizerInterface): Handles speaker diarization.
            aligner (AlignerInterface): Aligns transcriptions with speaker timestamps.
            data_saver (DataSaver): Saves intermediate results when in DEBUG mode.
        """
        self.downloader = downloader
        self.transcriber = transcriber
        self.diarizer = diarizer
        self.aligner = aligner
        self.data_saver = data_saver

    def process(self, echo_input: str):
        logger.debug("Downloading audio...")
        audio_path = self.downloader.download(echo_input)
        if not audio_path:
            return None
        
        logger.debug("Transcribing downloaded audio...")
        transcription, timestamps = self.transcriber.transcribe(audio_path)

        logger.debug("Diarizing downloaded audio...")
        diarization = self.diarizer.diarize(audio_path)

        # ✅ Enregistrer les étapes intermédiaires en mode DEBUG
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Saving intermediate debug files...")
            self.data_saver.save_data("debug_transcription.txt", transcription)
            self.data_saver.save_data("debug_timestamps.json", timestamps)
            self.data_saver.save_data("debug_diarization.txt", str(diarization))

        return self.aligner.align(transcription, timestamps, diarization)
