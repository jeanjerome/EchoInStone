"""Tests for the decoding options the transcriber hands to Whisper.

These options decide whether segment timestamps come back at all, which
decoder prompt is used, and whether the decoded text keeps its spacing. They
are set once at load time and never asserted on by the rest of the pipeline,
so a silent change in how they are passed only surfaces as degraded output on
a real recording.
"""

from unittest.mock import MagicMock, patch

import pytest

from EchoInStone.processing.whisper_audio_transcriber import WhisperAudioTranscriber


@pytest.fixture
def transcription_result():
    """The shape the ASR pipeline returns when timestamps are requested."""
    return {
        "text": " Mesdames, Messieurs, merci d'etre presents.",
        "chunks": [
            {"text": " Mesdames, Messieurs,", "timestamp": (0.0, 2.4)},
            {"text": " merci d'etre presents.", "timestamp": (2.4, 4.8)},
        ],
    }


@pytest.fixture
def transcriber(transcription_result):
    """A transcriber built against stubs, so no model is downloaded.

    The pipeline factory is patched rather than the pipeline it builds, so the
    arguments given at construction stay observable.
    """
    with (
        patch(
            "EchoInStone.processing.whisper_audio_transcriber.AutoModelForSpeechSeq2Seq"
        ) as auto_model,
        patch(
            "EchoInStone.processing.whisper_audio_transcriber.AutoProcessor"
        ) as auto_processor,
        patch("EchoInStone.processing.whisper_audio_transcriber.pipeline") as pipeline_factory,
    ):
        auto_model.from_pretrained.return_value = MagicMock()
        auto_processor.from_pretrained.return_value = MagicMock()
        pipeline_factory.return_value = MagicMock(return_value=transcription_result)

        instance = WhisperAudioTranscriber()
        instance.pipeline_factory = pipeline_factory
        yield instance


class TestDecodingOptions:
    """Where and how the decoding options reach Whisper."""

    def test_asks_for_segment_timestamps_on_each_call(self, transcriber):
        """Speaker alignment consumes segment timestamps, so they are required.

        Without them the pipeline returns text only, and alignment has nothing
        to attribute speakers to.
        """
        transcriber.transcribe("any/path.wav")

        _, kwargs = transcriber.pipe.call_args
        assert kwargs["return_timestamps"] is True

    def test_names_the_transcribe_task_on_each_call(self, transcriber):
        """Naming the task selects the decoder prompt through the supported flag.

        Left unset, the checkpoint falls back to the legacy forced_decoder_ids
        entry it carries, a path scheduled for removal upstream.
        """
        transcriber.transcribe("any/path.wav")

        _, kwargs = transcriber.pipe.call_args
        assert kwargs["task"] == "transcribe"

    def test_leaves_the_language_to_detection(self, transcriber):
        """Recordings come in several languages, so none may be assumed."""
        transcriber.transcribe("any/path.wav")

        _, kwargs = transcriber.pipe.call_args
        assert "language" not in kwargs

    def test_sets_no_decoding_options_at_construction(self, transcriber):
        """Options given to the factory are folded into the generation config.

        That is the deprecated path: it works today, but it is the one that
        stops taking effect without raising.
        """
        _, kwargs = transcriber.pipeline_factory.call_args
        assert "return_timestamps" not in kwargs
        assert "task" not in kwargs

    def test_opts_out_of_bpe_space_cleanup(self, transcriber):
        """Cleanup strips the space French requires ahead of " ! ? : ; "."""
        assert transcriber.processor.tokenizer.clean_up_tokenization_spaces is False


class TestTranscribe:
    """What the transcription stage hands to the caller."""

    def test_returns_the_text_and_the_segments(self, transcriber, transcription_result):
        """Both halves are consumed downstream: text for output, chunks for alignment."""
        text, chunks = transcriber.transcribe("any/path.wav")

        assert text == transcription_result["text"]
        assert chunks == transcription_result["chunks"]

    def test_returns_no_transcription_when_the_pipeline_raises(self, transcriber):
        """Errors are reported as an absent result rather than propagated."""
        transcriber.pipe = MagicMock(side_effect=RuntimeError("boom"))

        assert transcriber.transcribe("any/path.wav") == (None, None)
