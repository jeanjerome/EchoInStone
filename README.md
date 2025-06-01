# EchoInStone

**EchoInStone** is a comprehensive audio processing tool designed to transcribe, diarize, and align speaker segments from audio files with a focus on achieving the most accurate and faithful transcription possible. It supports various audio sources, including YouTube videos and podcasts, and provides a flexible pipeline for processing audio data, prioritizing precision and reliability over speed.

## Features

- **Transcription**: Convert audio files into text using state-of-the-art automatic speech recognition (ASR) model, `Whisper Large v3 Turbo`.
- **Diarization**: Identify and separate different speakers in an audio file with the cutting-edge model, `Pyannote Speaker Diarization 3.1`.
- **Alignment**: Align transcribed text with the corresponding audio segments using a customized algorithm tailored to be highly efficient and faithful to the outputs of Whisper and Pyannote, `SpeakerAlignement`.
- **Flexible and Extensible Pipeline**: Easily integrate new models or processing steps into an orchestrated pipeline, `AudioProcessingOrchestrator`.
- **Multiple Deployment Options**: Deploy as CLI tool, serverless function (AWS Lambda), containerized service (Kubernetes), or HTTP API.

## Deployment Options

EchoInStone currently supports CLI mode for production use, with additional deployment patterns provided as reference implementations:

- **CLI Mode** ✅ **Production Ready**: Traditional command-line interface for local processing
- **Serverless Mode** 🚧 **Example Implementation**: AWS Lambda functions for scalable cloud processing
- **Container Mode** 🚧 **Example Implementation**: Kubernetes pods for microservice architectures  
- **HTTP API Mode** 🚧 **Example Implementation**: RESTful web service for integration with other applications

> **Note**: Only CLI mode is fully supported and tested for production use. Other deployment modes are provided as architectural examples and proof-of-concept implementations that may require additional configuration and testing for production environments.

> Note: The current version of EchoInStone is a preliminary release. Future updates will include more flexible configuration options and enhanced functionality.

## Installation

### Prerequisites

- Python 3.11 or higher
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
   - The logging configuration is set up to output logs to both the console and a file (`app.log`). You can modify the logging settings in `logging_config.py`.

4. **Configure Hugging Face Token**:

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

### CLI Mode (Command Line Interface)

To transcribe and diarize a YouTube video, you can run the following command:

```bash
poetry run python main.py <audio_input_url>
```

- `<audio_input_url>`: The URL of the audio input (YouTube, podcast, or direct audio file).

#### Command-Line Arguments

- **`--output_dir`**: Directory to save the output files. Default is `"results"`.
  ```bash
  poetry run python main.py <audio_input_url> --output_dir <output_directory>
  ```

- **`--transcription_output`**: Filename for the transcription output. Default is `"speaker_transcriptions.json"`.
  ```bash
  poetry run python main.py <audio_input_url> --transcription_output <output_filename>
  ```

#### CLI Examples

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

### Serverless Mode (Example Implementation)

> ⚠️ **Development Status**: These are reference implementations for demonstration purposes. Additional testing and configuration may be required for production use.

#### AWS Lambda

```python
from serverless.handler import lambda_handler

event = {
    "echo_input": "https://www.youtube.com/watch?v=plZRCMx_Jd8",
    "output_dir": "/tmp/results"  # optional
}

result = lambda_handler(event, context)
```

#### Kubernetes Pod

```python
from serverless.handler import kubernetes_handler

request_data = {
    "echo_input": "https://www.youtube.com/watch?v=plZRCMx_Jd8",
    "output_dir": "/app/results"  # optional
}

result = kubernetes_handler(request_data)
```

#### HTTP API

Start the HTTP server:
```bash
python serverless/handler.py
```

Send a POST request:
```bash
curl -X POST http://localhost:5000/process \
  -H "Content-Type: application/json" \
  -d '{
    "echo_input": "https://www.youtube.com/watch?v=plZRCMx_Jd8",
    "output_dir": "results"
  }'
```

Health check:
```bash
curl http://localhost:5000/health
```

### Programmatic Usage

```python
from EchoInStone.app import EchoInStoneApp

# Initialize the application
app = EchoInStoneApp(output_dir="results")

# Process audio (asynchronous)
transcriptions = app.process_audio(
    echo_input="https://www.youtube.com/watch?v=plZRCMx_Jd8",
    transcription_output="output.json"
)

# Process audio (synchronous, returns dict)
result = app.process_audio_sync(
    echo_input="https://www.youtube.com/watch?v=plZRCMx_Jd8"
)
```

## Testing

EchoInStone includes comprehensive test coverage with both unit tests and BDD (Behavior-Driven Development) tests to ensure reliability and prevent regressions.

### Run All Tests

To run all tests (unit tests and BDD tests):
```bash
poetry run pytest tests/ features/ -v
```

### Run Tests by Type

**Unit Tests Only** (technical implementation tests):
```bash
poetry run pytest tests/ -v
```

**BDD Tests Only** (behavioral scenarios):
```bash
poetry run pytest features/ -v
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
  - `test_downloader_factory.py`: Tests for downloader selection logic
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

## Deployment (Example Configurations)

> ⚠️ **Important**: The following deployment configurations are provided as examples and starting points. They may require additional customization, security hardening, and testing for production environments.

### Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY pyproject.toml poetry.lock ./
COPY serverless/requirements.txt ./serverless/
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev && \
    pip install -r serverless/requirements.txt

# Copy application code
COPY . .

# Expose port for HTTP API
EXPOSE 5000

# Default command (can be overridden)
CMD ["python", "serverless/handler.py"]
```

Build and run:
```bash
docker build -t echoinstone .
docker run -p 5000:5000 echoinstone
```

### Kubernetes

Create a deployment manifest:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: echoinstone
spec:
  replicas: 2
  selector:
    matchLabels:
      app: echoinstone
  template:
    metadata:
      labels:
        app: echoinstone
    spec:
      containers:
      - name: echoinstone
        image: echoinstone:latest
        ports:
        - containerPort: 5000
        env:
        - name: LOG_LEVEL
          value: "INFO"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
---
apiVersion: v1
kind: Service
metadata:
  name: echoinstone-service
spec:
  selector:
    app: echoinstone
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
```

Deploy:
```bash
kubectl apply -f echoinstone-deployment.yaml
```

### AWS Lambda

Package and deploy using AWS SAM or Serverless Framework:

```yaml
# serverless.yml
service: echoinstone

provider:
  name: aws
  runtime: python3.11
  timeout: 900  # 15 minutes
  memorySize: 3008

functions:
  process:
    handler: serverless.handler.lambda_handler
    events:
      - http:
          path: process
          method: post
```

## Configuration

### Environment Variables

- **`LOG_LEVEL`**: Set logging level (DEBUG, INFO, WARNING, ERROR). Default: INFO
- **`HUGGING_FACE_TOKEN`**: Your Hugging Face authentication token (required)
- **`OUTPUT_DIR`**: Default output directory for processed files

### Logging

Logging is configured to output messages to both the console and a file (`app.log`). You can adjust the logging level using the `LOG_LEVEL` environment variable or by modifying the `logging_config.py` file.

### Models

- **Transcription Model**: The default transcription model is `openai/whisper-large-v3-turbo`. You can change this by modifying the `model_name` parameter in the `WhisperAudioTranscriber` initialization.
- **Diarization Model**: The default diarization model is `pyannote/speaker-diarization-3.1`. You can change this by modifying the model loading code in the `PyannoteDiarizer` class.

### Performance Tuning

For CLI deployments:
- Ensure sufficient RAM (2-4 GB recommended) for audio processing
- Use SSD storage for faster temporary file operations
- Consider using GPU acceleration for Whisper if available

For experimental serverless deployments:
- **Memory**: Recommend 2-4 GB for optimal performance
- **Timeout**: Set to 15 minutes or more for longer audio files
- **CPU**: Multi-core instances recommended for faster processing
- **Note**: Resource requirements may vary significantly based on audio length and quality

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
