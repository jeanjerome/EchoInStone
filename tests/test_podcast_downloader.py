"""Unit tests for PodcastDownloader.

Covers two regressions observed when running the real pipeline:
1. download() returned True instead of the file path, so transcribe()/diarize()
   received a bool.
2. The sanitization regex stripped path separators, so the file was written
   in the CWD instead of inside output_dir.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from EchoInStone.capture.podcast_downloader import PodcastDownloader


def _fake_feed(title: str, audio_url: str = "https://example.com/episode.mp3") -> MagicMock:
    enclosure = MagicMock()
    enclosure.rel = "enclosure"
    enclosure.href = audio_url
    entry = MagicMock()
    entry.title = title
    entry.links = [enclosure]
    feed = MagicMock()
    feed.entries = [entry]
    return feed


@pytest.fixture
def temp_output_dir() -> str:
    with tempfile.TemporaryDirectory() as d:
        yield d


@pytest.fixture(autouse=True)
def _stub_audio_segment():
    """Mock pydub by default so synthetic bytes don't crash ffmpeg.

    Tests that need real conversion behavior can override via their own patch.
    """
    fake_segment = MagicMock()

    def fake_export(out_path: str, format: str) -> None:  # noqa: A002
        with open(out_path, "wb") as f:
            f.write(b"RIFF....WAVE")

    fake_segment.export.side_effect = fake_export
    with patch(
        "EchoInStone.capture.podcast_downloader.AudioSegment.from_file",
        return_value=fake_segment,
    ):
        yield


def test_download_returns_path_to_saved_file(temp_output_dir: str) -> None:
    downloader = PodcastDownloader(output_dir=temp_output_dir)

    response = MagicMock()
    response.content = b"\x00\x01\x02fake-mp3-bytes"
    response.raise_for_status = MagicMock()

    with patch(
        "EchoInStone.capture.podcast_downloader.feedparser.parse",
        return_value=_fake_feed(title="Hello World"),
    ), patch(
        "EchoInStone.capture.podcast_downloader.requests.get",
        return_value=response,
    ):
        result = downloader.download("https://example.com/feed.xml")

    assert isinstance(result, str), f"Expected path string, got {type(result).__name__}"
    assert os.path.isfile(result), f"Expected file to exist at {result}"


def test_download_writes_inside_output_dir(temp_output_dir: str) -> None:
    """The output_dir separator must survive sanitization."""
    downloader = PodcastDownloader(output_dir=temp_output_dir)

    response = MagicMock()
    response.content = b"data"
    response.raise_for_status = MagicMock()

    with patch(
        "EchoInStone.capture.podcast_downloader.feedparser.parse",
        return_value=_fake_feed(title="Episode With Spaces"),
    ), patch(
        "EchoInStone.capture.podcast_downloader.requests.get",
        return_value=response,
    ):
        result = downloader.download("https://example.com/feed.xml")

    parent = Path(result).resolve().parent
    expected_parent = Path(temp_output_dir).resolve()
    assert parent == expected_parent, (
        f"File written outside output_dir: parent={parent}, expected={expected_parent}"
    )


def test_download_sanitizes_unsafe_chars_in_title(temp_output_dir: str) -> None:
    downloader = PodcastDownloader(output_dir=temp_output_dir)

    response = MagicMock()
    response.content = b"data"
    response.raise_for_status = MagicMock()

    with patch(
        "EchoInStone.capture.podcast_downloader.feedparser.parse",
        return_value=_fake_feed(title="Euphoria saison 3 (fiction nulle?)"),
    ), patch(
        "EchoInStone.capture.podcast_downloader.requests.get",
        return_value=response,
    ):
        result = downloader.download("https://example.com/feed.xml")

    name = Path(result).name
    for forbidden in ["(", ")", "?", " "]:
        assert forbidden not in name, f"Unsanitized {forbidden!r} in {name!r}"


def test_download_replaces_unicode_whitespace(temp_output_dir: str) -> None:
    """Non-breaking spaces (NBSP) and other unicode whitespace must not survive."""
    downloader = PodcastDownloader(output_dir=temp_output_dir)

    response = MagicMock()
    response.content = b"data"
    response.raise_for_status = MagicMock()

    title_with_nbsp = "Euphoria saison 3 _ putes partout"
    with patch(
        "EchoInStone.capture.podcast_downloader.feedparser.parse",
        return_value=_fake_feed(title=title_with_nbsp),
    ), patch(
        "EchoInStone.capture.podcast_downloader.requests.get",
        return_value=response,
    ):
        result = downloader.download("https://example.com/feed.xml")

    name = Path(result).name
    assert " " not in name, f"NBSP leaked into filename: {name!r}"
    assert " " not in name, f"Plain space leaked into filename: {name!r}"


def test_download_returns_wav_path(temp_output_dir: str) -> None:
    """Pyannote/Whisper consume WAV uniformly; podcast hosts often serve M4A
    behind .mp3 URLs. The downloader must convert before returning."""
    downloader = PodcastDownloader(output_dir=temp_output_dir)

    response = MagicMock()
    response.content = b"fake-audio-bytes"
    response.raise_for_status = MagicMock()

    fake_segment = MagicMock()

    def fake_export(out_path: str, format: str) -> None:  # noqa: A002 (mirrors pydub API)
        with open(out_path, "wb") as f:
            f.write(b"RIFF....WAVE")

    fake_segment.export.side_effect = fake_export

    with patch(
        "EchoInStone.capture.podcast_downloader.feedparser.parse",
        return_value=_fake_feed(title="Some Episode"),
    ), patch(
        "EchoInStone.capture.podcast_downloader.requests.get",
        return_value=response,
    ), patch(
        "EchoInStone.capture.podcast_downloader.AudioSegment.from_file",
        return_value=fake_segment,
    ):
        result = downloader.download("https://example.com/feed.xml")

    assert result is not None
    assert result.endswith(".wav"), f"Expected .wav suffix, got {result!r}"
    assert os.path.isfile(result)


def test_download_returns_none_when_no_enclosure() -> None:
    downloader = PodcastDownloader(output_dir="unused")

    feed = MagicMock()
    feed.entries = []

    with patch(
        "EchoInStone.capture.podcast_downloader.feedparser.parse",
        return_value=feed,
    ):
        result = downloader.download("https://example.com/feed.xml")

    assert result is None


def test_download_returns_none_on_request_error(temp_output_dir: str) -> None:
    downloader = PodcastDownloader(output_dir=temp_output_dir)

    with patch(
        "EchoInStone.capture.podcast_downloader.feedparser.parse",
        return_value=_fake_feed(title="Boom"),
    ), patch(
        "EchoInStone.capture.podcast_downloader.requests.get",
        side_effect=RuntimeError("network down"),
    ):
        result = downloader.download("https://example.com/feed.xml")

    assert result is None
