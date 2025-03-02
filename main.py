import argparse
import logging
from EchoInStone.utils import configure_logging
from EchoInStone.echoinstone_app import EchoInStoneApp

# Configure logging
configure_logging(logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    """
    Entry point (as a CLI) for EchoInStone audio processing app.
    """
    parser = argparse.ArgumentParser(description="EchoInStone Audio Processing CLI")
    parser.add_argument("audio_source", type=str, help="Source of the audio input (YouTube URL, podcast link, or local file)")
    parser.add_argument("--save_dir", type=str, default="results", help="Directory to save the output files")
    parser.add_argument("--transcript_file", type=str, default="speaker_transcriptions.json", help="Filename for the transcription output")

    args = parser.parse_args()

    app = EchoInStoneApp(args.save_dir)
    result = app.run(args.audio_source)

    if result:
        app.save_results(args.transcript_file, result)
    else:
        logger.warning("No transcriptions were generated.")

if __name__ == "__main__":
    main()
