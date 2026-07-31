# EchoInStone

**EchoInStone** is a comprehensive audio processing tool designed to transcribe, diarize, and align speaker segments from audio files with a focus on achieving the most accurate and faithful transcription possible. It supports various audio sources, including YouTube videos and podcasts, and provides a flexible pipeline for processing audio data, prioritizing precision and reliability over speed.

## Features

- **Transcription**: Convert audio files into text using state-of-the-art automatic speech recognition (ASR) model, `Whisper Large v3 Turbo`.
- **Diarization**: Identify and separate different speakers in an audio file with the cutting-edge model, `Pyannote Speaker Diarization 3.1`.
- **Alignment**: Align transcribed text with the corresponding audio segments using a customized algorithm tailored to be highly efficient and faithful to the outputs of Whisper and Pyannote, `SpeakerAlignement`.
- **Flexible and Extensible Pipeline**: Easily integrate new models or processing steps into an orchestrated pipeline, `AudioProcessingOrchestrator`.

> Note: The current version of EchoInStone is a preliminary release. Future updates will include more flexible configuration options and enhanced functionality.

## Installation

### Prerequisites

- Python 3.11 or 3.12
- Poetry (dependency management tool)
- ffmpeg (required for audio processing)

> Note: `ffmpeg` must be installed and available in your system's PATH.  
> You can install it via your package manager:
> - On macOS: `brew install ffmpeg`
> - On Ubuntu/Debian: `sudo apt install ffmpeg`
> - On Windows: Download from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)

### Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jeanjerome/EchoInStone.git
   cd EchoInStone
   ```

2. **Install dependencies using Poetry**:
   ```bash
   poetry install
   ```

3. **Configure logging** (optional):
   - The logging configuration is set up to output logs to both the console and a file (`app.log`). You can modify the logging settings in `EchoInStone/utils/logging_config.py`.

4. **Authenticate with Hugging Face**:

   The diarization model is gated, so it needs a Hugging Face credential. Create a token at [Hugging Face Settings](https://huggingface.co/settings/tokens), then either log in once:

   ```bash
   huggingface-cli login
   ```

   or export the token in your environment:

   ```bash
   export HF_TOKEN=hf_your_token_here
   ```

   Either way the token is read by `huggingface_hub` and never stored in the repository. Visit the [model page](https://huggingface.co/pyannote/speaker-diarization-3.1) once to accept its conditions, otherwise the download is refused whatever the credential.

## Usage

### Basic Example

To transcribe and diarize a YouTube video, you can run the following command:

```bash
poetry run python main.py <audio_input_url>
```

- `<audio_input_url>`: The URL of the audio input (YouTube, podcast, or direct audio file).

### Command-Line Arguments

- **`--output_dir`**: Directory to save the output files. Default is `"results"`.
  ```bash
  poetry run python main.py <audio_input_url> --output_dir <output_directory>
  ```

- **`--transcription_output`**: Filename for the transcription output. Default is `"speaker_transcriptions.json"`.
  ```bash
  poetry run python main.py <audio_input_url> --transcription_output <output_filename>
  ```

### Examples

- **Transcribe and diarize a YouTube video**:
  ```bash
  poetry run python main.py "https://www.youtube.com/watch?v=plZRCMx_Jd8"
  ```

- **Transcribe and diarize a podcast**:
  ```bash
  poetry run python main.py "https://radiofrance-podcast.net/podcast09/rss_13957.xml"
  ```

- **Transcribe and diarize a direct MP3 file**:
  ```bash
  poetry run python main.py "https://media.radiofrance-podcast.net/podcast09/25425-13.02.2025-ITEMA_24028677-2025C53905E0006-NET_MFC_D378B90D-D570-44E9-AB5A-F0CC63B05A14-21.mp3"
  ```

## Testing

EchoInStone includes comprehensive test coverage with both unit tests and BDD (Behavior-Driven Development) tests to ensure reliability and prevent regressions.

### Run All Tests

To run all tests (unit tests and BDD tests):
```bash
poetry run pytest tests/ features/ -v
```

`pytest.ini` collects both directories by default, so a bare `poetry run pytest` runs the same set.

### Run Tests by Type

**Unit Tests Only** (technical implementation tests):
```bash
poetry run pytest tests/ -v
```

**BDD Tests Only** (behavioral scenarios):
```bash
poetry run pytest features/ -v
```

One scenario downloads a real video and is marked `youtube`. YouTube answers datacenter addresses with a bot challenge, so it passes from a workstation but not from a hosted CI runner, where it is deselected. To run it alone, or to leave it out locally:

```bash
poetry run pytest features/ -v -m youtube        # that scenario only
poetry run pytest features/ -v -m "not youtube"  # everything else, as CI runs it
```

### Test Coverage

To generate a coverage report:
```bash
poetry run pytest tests/ features/ --cov=EchoInStone --cov-report html
```

The coverage report will be generated in the `htmlcov/` directory.

### Test Structure

- **`tests/`**: Unit tests that verify individual components and functions
  - `test_audio_downloader.py`: Tests for URL/file downloading functionality
  - `test_podcast_downloader.py`: Tests for RSS feed parsing and episode selection
  - `test_downloader_factory.py`: Tests for downloader selection logic
  - `test_whisper_audio_transcriber.py`: Tests for the decoding options passed to Whisper
  - `test_pyannote_diarizer.py`: Tests for the diarization stage and its join to alignment
  - `test_logging_config.py`: Tests for the log levels applied to third-party libraries
  - `test_integration.py`: Integration tests for complete workflows

- **`features/`**: BDD tests that describe user-facing behavior
  - `downloader.feature`: Downloader selection scenarios
  - `audio_download.feature`: Audio download functionality scenarios
  - `successful_download.feature`: Download success scenarios
  - `invalid_url.feature`: Error handling scenarios
  - `transcription_output.feature`: Transcription output validation

### Test Examples

The test suite covers various scenarios including:
- YouTube video downloads
- Podcast RSS feed processing
- Direct MP3/audio file URLs (including RFI radio content)
- Local file processing
- Network error handling
- Header authentication for restricted URLs

All tests are designed to prevent regressions and ensure that the audio download functionality works correctly across different input types.

### Continuous Integration

Every pull request runs `.github/workflows/ci.yml`: lock file consistency (`poetry check --lock`), unit tests on Python 3.11 and 3.12, and the BDD suite. The BDD suite runs as its own job because it downloads the Whisper weights; both the virtualenv and the model cache are keyed so repeat runs stay cheap.

## Configuration

### Logging

Logging is configured to output messages to both the console and a file (`app.log`). You can adjust the logging level and format in the `EchoInStone/utils/logging_config.py` file.

Third-party libraries are quieted above `DEBUG`: resolving a model on the Hugging Face hub emits dozens of request lines that would otherwise bury the pipeline's own progress. Running at `DEBUG` restores them.

### Models

- **Transcription Model**: The default transcription model is `openai/whisper-large-v3-turbo`. You can change this by modifying the `model_name` parameter in the `WhisperAudioTranscriber` initialization.
- **Diarization Model**: The default diarization model is `pyannote/speaker-diarization-3.1`. You can change this by modifying the model loading code in the `PyannoteDiarizer` class. Its successor `speaker-diarization-community-1` was evaluated and set aside: it segments more finely, and on a long interview dominated by one voice that granularity split sentences and credited them to the wrong speaker more often than it resolved genuine interjections.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to the open-source community for the various libraries and models used in this project.
- Special thanks to the contributors and maintainers of the models and tools that make this project possible.

## Contact

For any questions or suggestions, please open an issue.
