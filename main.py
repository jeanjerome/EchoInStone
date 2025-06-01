import argparse
from EchoInStone.utils import configure_logging
import logging
from EchoInStone.app import EchoInStoneApp

# Configure logging
configure_logging(logging.INFO)
logger = logging.getLogger(__name__)


# Youtube = 'https://www.youtube.com/watch?v=ipXG9iQq-Tw'
# Podcast = 'https://radiofrance-podcast.net/podcast09/rss_13957.xml'

# Test Youtube video = 'https://www.youtube.com/watch?v=plZRCMx_Jd8'
# Test Podcast = 'https://radiofrance-podcast.net/podcast09/rss_13957.xml'
# Test MP3 File = 'https://media.radiofrance-podcast.net/podcast09/25425-13.02.2025-ITEMA_24028677-2025C53905E0006-NET_MFC_D378B90D-D570-44E9-AB5A-F0CC63B05A14-21.mp3'


def main(echo_input, output_dir, transcription_output):
    """
    Main function to orchestrate the audio processing pipeline.
    """
    app = EchoInStoneApp(output_dir=output_dir)
    app.process_audio(echo_input, transcription_output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="EchoInStone Audio Processing CLI")
    parser.add_argument("echo_input", type=str, help="URL of the audio input (YouTube, podcast, or direct audio file)")
    parser.add_argument("--output_dir", type=str, default="results", help="Directory to save the output files")
    parser.add_argument("--transcription_output", type=str, default="speaker_transcriptions.json", help="Filename for the transcription output")

    args = parser.parse_args()

    main(args.echo_input, args.output_dir, args.transcription_output)