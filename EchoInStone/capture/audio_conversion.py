import logging
import shutil
import subprocess

logger = logging.getLogger(__name__)


def convert_to_wav(source_path: str, wav_path: str) -> None:
    """Decode an audio file and re-encode it as WAV.

    The transcription and diarization pipelines consume WAV uniformly, while
    sources arrive in whatever container the host served. ffmpeg decodes the
    source and writes 16-bit PCM at the source sample rate and channel count.

    Args:
        source_path: Path to the source audio, in any format ffmpeg decodes.
        wav_path: Path the WAV file is written to, overwritten if it exists.

    Raises:
        RuntimeError: If ffmpeg is absent from PATH, or fails to decode the source.
    """
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg is None:
        raise RuntimeError(
            "ffmpeg was not found in PATH; it is required to convert audio to WAV"
        )

    result = subprocess.run(
        [ffmpeg, "-y", "-loglevel", "error", "-i", source_path, wav_path],
        capture_output=True,
    )
    if result.returncode != 0:
        stderr = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"ffmpeg failed to convert {source_path}: {stderr}")

    logger.debug(f"Converted {source_path} to {wav_path}")
