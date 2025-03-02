import os
import re
import logging
import numpy as np
import librosa
import noisereduce as nr
from pydub import AudioSegment
from scipy.signal import butter, lfilter

logger = logging.getLogger(__name__)

class AudioUtils:
    @staticmethod
    def clean_filename(file_path: str, new_extension: str = "mp3") -> str:
        """
        Cleans up the filename by removing special characters and spaces.

        Args:
            file_path (str): The original file path.
            new_extension (str): The extension for the cleaned file. Default is "mp3".

        Returns:
            str: The new sanitized file path.
        """
        dir_path, base_name = os.path.split(file_path)
        base, ext = os.path.splitext(base_name)
        safe_base = re.sub(r'[^\w\s-]', '', base).replace(' ', '_')
        new_file = os.path.join(dir_path, f"{safe_base}.{new_extension}")
        
        os.rename(file_path, new_file)
        logger.debug(f"Renamed file to {new_file}")

        return new_file

    @staticmethod
    def butter_highpass_filter(data, cutoff, fs, order=5):
        """
        Apply a high-pass Butterworth filter.

        Args:
            data (numpy.array): Audio signal.
            cutoff (int): Cutoff frequency in Hz.
            fs (int): Sampling rate in Hz.
            order (int): Order of the filter.

        Returns:
            numpy.array: Filtered audio signal.
        """
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype='high', analog=False)
        return lfilter(b, a, data)

    @staticmethod
    def convert_to_wav(input_file: str) -> str:
        """
        Converts an audio file to WAV format with CD-quality settings (Mono, 44.1kHz, 16-bit PCM).

        Args:
            input_file (str): Path to the input audio file.

        Returns:
            str: Path to the WAV file.
        """
        dir_path, base_name = os.path.split(input_file)
        base, ext = os.path.splitext(base_name)
        wav_file = os.path.join(dir_path, f"{base}.wav")

        audio = AudioSegment.from_file(input_file)
        audio = audio.set_channels(1).set_frame_rate(44100).set_sample_width(2)
        audio.export(wav_file, format="wav")

        logger.debug(f"Converted {input_file} to WAV: {wav_file} (Mono, 44.1kHz, 16-bit PCM)")
        return wav_file

    @staticmethod
    def convert_to_wav_filtered(input_file: str) -> str:
        """
        Converts an audio file to WAV format (Mono, 44.1kHz, 16-bit PCM).
        Applies filtering (high-pass, noise reduction, normalization).

        Args:
            input_file (str): Path to the input audio file.

        Returns:
            str: Path to the processed WAV file.
        """
        dir_path, base_name = os.path.split(input_file)
        base, ext = os.path.splitext(base_name)
        wav_file = os.path.join(dir_path, f"{base}_filtered.wav")

        # Load audio with librosa
        y, sr = librosa.load(input_file, sr=44100, mono=True)

        # Apply high-pass filter to remove low-frequency noise
        y_filtered = AudioUtils.butter_highpass_filter(y, cutoff=80, fs=sr)

        # Apply noise reduction
        y_denoised = nr.reduce_noise(y=y_filtered, sr=sr, prop_decrease=0.5)

        # Normalize audio manually
        y_denoised = y_denoised / np.max(np.abs(y_denoised))

        # Convert back to int16 PCM format
        y_denoised = (y_denoised * 32767).astype(np.int16)

        # Convert NumPy array to Pydub AudioSegment
        audio_segment = AudioSegment(
            y_denoised.tobytes(),
            frame_rate=sr,
            sample_width=2,
            channels=1
        )

        # Export the processed WAV file
        audio_segment.export(wav_file, format="wav")

        logger.debug(f"Converted {input_file} to WAV (filtered): {wav_file} (Mono, 44.1kHz, 16-bit PCM)")
        return wav_file
