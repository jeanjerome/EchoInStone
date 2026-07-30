"""Tests for the diarization stage and the shape it hands to alignment.

The diarization pipeline returns a container object, while alignment consumes a
pyannote Annotation. These tests pin that unwrapping down, because a mismatch
here surfaces only when a real audio file runs all the way through.
"""

from unittest.mock import MagicMock, patch

import pytest
from pyannote.audio.pipelines.speaker_diarization import DiarizeOutput
from pyannote.core import Annotation, Segment

from EchoInStone.processing.pyannote_diarizer import PyannoteDiarizer
from EchoInStone.processing.speaker_aligner import SpeakerAligner


def build_annotation(turns):
    """Build an Annotation from (start, end, speaker) triples."""
    annotation = Annotation()
    for start, end, speaker in turns:
        annotation[Segment(start, end)] = speaker
    return annotation


@pytest.fixture
def diarize_output():
    """Build the real container the pipeline returns, holding two annotations.

    The concrete class is used rather than a stand-in so that a future change to
    its shape breaks these tests, and so the failure seen when the container
    leaks through to alignment is the one production raises.

    The exclusive annotation drops the overlap between the two speakers, which
    is the distinction the diarizer relies on when it picks one to return.
    """
    return DiarizeOutput(
        speaker_diarization=build_annotation(
            [(0.0, 5.0, "SPEAKER_00"), (4.0, 9.0, "SPEAKER_01")]
        ),
        exclusive_speaker_diarization=build_annotation(
            [(0.0, 4.0, "SPEAKER_00"), (5.0, 9.0, "SPEAKER_01")]
        ),
    )


@pytest.fixture
def diarizer(diarize_output):
    """A diarizer whose pipeline is stubbed out, so no model is downloaded."""
    with patch.object(PyannoteDiarizer, "__init__", lambda self: None):
        instance = PyannoteDiarizer()
    instance.pipeline = MagicMock(return_value=diarize_output)
    return instance


class TestPyannoteDiarizer:
    """Behaviour of the diarization stage."""

    def test_returns_an_annotation_not_the_container(self, diarizer):
        """Alignment calls itersegments and itertracks on whatever comes back.

        Returning the container instead of the annotation raises AttributeError
        only once a real file reaches alignment, well past the point where a
        wrong return type is cheap to notice.
        """
        result = diarizer.diarize("any/path.wav")

        assert isinstance(result, Annotation)
        assert hasattr(result, "itersegments")
        assert hasattr(result, "itertracks")

    def test_returns_the_overlap_free_annotation(self, diarizer, diarize_output):
        """Alignment attributes one speaker per segment, so turns must not overlap."""
        result = diarizer.diarize("any/path.wav")

        assert result == diarize_output.exclusive_speaker_diarization
        assert result != diarize_output.speaker_diarization

    def test_returns_none_when_pipeline_is_unavailable(self, diarizer):
        """A pipeline that failed to load yields no diarization rather than raising."""
        diarizer.pipeline = None

        assert diarizer.diarize("any/path.wav") is None

    def test_returns_none_when_pipeline_raises(self, diarizer):
        """Errors during diarization are reported as an absent result."""
        diarizer.pipeline = MagicMock(side_effect=RuntimeError("boom"))

        assert diarizer.diarize("any/path.wav") is None


class TestDiarizerAlignerContract:
    """The join between diarization and alignment, which the unit tests miss."""

    def test_alignment_consumes_the_diarizer_output(self, diarizer):
        """Run a transcript through alignment using the real diarizer return value.

        This is the path that broke: each stage was individually sound, but the
        object handed across the boundary had changed shape.
        """
        timestamps = [
            {"text": "premiere partie", "timestamp": (0.0, 3.5)},
            {"text": "seconde partie", "timestamp": (5.5, 8.5)},
        ]

        diarization = diarizer.diarize("any/path.wav")
        aligned = SpeakerAligner().align("ignored", timestamps, diarization)

        assert [segment[0] for segment in aligned] == ["SPEAKER_00", "SPEAKER_01"]
        assert [segment[3] for segment in aligned] == [
            "premiere partie",
            "seconde partie",
        ]

    def test_alignment_handles_an_open_ended_final_segment(self, diarizer):
        """Whisper leaves the last timestamp open when audio ends mid-segment.

        Alignment substitutes the end of the last diarization turn, which is
        only reachable when the diarization result exposes itersegments.
        """
        timestamps = [{"text": "fin", "timestamp": (5.5, None)}]

        diarization = diarizer.diarize("any/path.wav")
        aligned = SpeakerAligner().align("ignored", timestamps, diarization)

        assert len(aligned) == 1
        assert aligned[0][0] == "SPEAKER_01"
        assert aligned[0][2] == 9.0
