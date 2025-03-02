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

- Python 3.12
- Conda

### Steps

#### 1. **Clone the repository**:
   ```bash
   git clone https://github.com/jeanjerome/EchoInStone.git
   cd EchoInStone
   ```

#### **2. Setting up the environment and installing dependencies**

On macOS, some dependencies like `librosa` can be difficult to install directly with Poetry due to compatibility issues with low-level libraries (e.g., `llvmlite`, `numba`). To ensure a smooth installation, we use **Conda** to manage system-level dependencies and let **Poetry** handle the rest.

##### **🔹 Step-by-step setup**
1. **Create a Conda environment and install Python**  
   We create a Conda environment named `echoinstone` with Python 3.12:  
   ```bash
   conda create -n echoinstone python=3.12 -y
   conda activate echoinstone
   ```

2. **Install system-critical dependencies via Conda**  
   Some packages, like `librosa`, rely on compiled libraries that Conda manages more efficiently than Poetry:  
   ```bash
   conda install -c conda-forge librosa
   conda install -c conda-forge numba
   ```

3. **Install Poetry inside the Conda environment**  
   Poetry will be used to manage all other dependencies:  
   ```bash
   pip install poetry
   ```

4. **Disable Poetry's virtual environment creation**  
   Since we're using Conda as our environment manager, we tell Poetry **not to create its own virtual environment**:  
   ```bash
   poetry config virtualenvs.create false
   ```

5. **Install the remaining dependencies with Poetry**  
   Finally, install all project dependencies using Poetry:  
   ```bash
   poetry install
   ```

> ✅ **With this setup, Conda efficiently handles system-dependent packages, while Poetry manages Python dependencies in a clean and structured way.**  
> 🚀 **This approach prevents installation conflicts and ensures cross-platform compatibility.**  

#### **3. Configure logging** (optional):
   - The logging configuration is set up to output logs to both the console and a file (`app.log`). You can modify the logging settings in `logging_config.py`.

#### **4. Configure Hugging Face Token**:

  - Add your Hugging Face token to this file. You can obtain a token by following these steps:
     1. Go to [Hugging Face Settings](https://huggingface.co/settings/tokens).
     2. Click on "New token".
     3. Copy the generated token and paste it into the `EchoInStone/config.py` file as shown below:

```python
# EchoInStone/config.py

# Hugging Face authentication token
HUGGING_FACE_TOKEN = "your_token_here"
```

## Usage

### Basic Example

Run the application inside the Conda environment:

```bash
conda activate echoinstone
python main.py <audio_source>
```

Or, if you prefer to explicitly use Poetry:

```bash
conda activate echoinstone
poetry run python main.py <audio_source>
```

- `<audio_source>`: The URL of the audio input (YouTube, podcast, direct audio file, or local file path).

### Command-Line Arguments

- **`--save_dir`**: Directory to save the output files. Default is `"results"`.
  ```bash
  poetry run python main.py <audio_source> --save_dir <output_directory>
  ```

- **`--transcript_file`**: Filename for the transcription output. Default is `"speaker_transcriptions.json"`.
  ```bash
  poetry run python main.py <audio_source> --transcript_file <output_filename>
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

- **Transcribe and diarize a local audio file**:
  ```bash
  poetry run python main.py "/path/to/local/audio.wav"
  ```

## Testing

To run the tests, use the following command:
```bash
poetry run pytest
```

This command will execute all the tests, including BDD tests, to ensure the functionality of the application.

## Configuration

### Logging

Logging is configured to output messages to both the console and a file (`app.log`). You can adjust the logging level and format in the `logging_config.py` file.

### Models

- **Transcription Model**: The default transcription model is `openai/whisper-large-v3-turbo`. You can change this by modifying the `model_name` parameter in the `WhisperAudioTranscriber` initialization.
- **Diarization Model**: The default diarization model is `pyannote/speaker-diarization-3.1`. You can change this by modifying the model loading code in the `PyannoteDiarizer` class.

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
