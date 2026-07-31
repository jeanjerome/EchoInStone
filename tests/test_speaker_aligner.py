"""Tests for how a transcript segment is credited to a speaker.

Diarization returns turns; transcription returns segments; neither lines up
with the other. Attribution therefore rests on which speaker occupies a
segment, and a finely segmented diarization makes that question sharp: one
answer arrives split into many turns with brief interjections threaded
through it. Comparing turns one at a time lets a fraction of a second carry
off a whole sentence, which reads as the wrong person speaking.
"""

from pyannote.core import Annotation, Segment

from EchoInStone.processing.speaker_aligner import SpeakerAligner


def build_annotation(turns):
    """Build an Annotation from (start, end, speaker) triples."""
    annotation = Annotation()
    for start, end, speaker in turns:
        annotation[Segment(start, end)] = speaker
    return annotation


class TestAttribution:
    """Which speaker a transcript segment is credited to."""

    def test_an_interjection_does_not_carry_off_the_segment(self):
        """Modelled on a real exchange, where a sentence changed hands.

        The guest answers in bursts while the host drops in acknowledgements,
        one of them longer than any single burst. The guest occupies more of
        the segment overall, so the sentence is theirs; comparing turns one at
        a time awards it to the host on the strength of that one interjection,
        cutting the answer mid-thought.

        Occupancy is 2.5s against 2.0s here. In the recording this came from it
        was 1.12s against 1.00s, close enough that float noise decided the
        outcome — the margin is not what makes turn-by-turn comparison wrong.
        """
        diarization = build_annotation(
            [
                (0.0, 0.5, "SPEAKER_01"),
                (0.5, 0.8, "SPEAKER_00"),
                (0.8, 1.3, "SPEAKER_01"),
                (1.3, 1.6, "SPEAKER_00"),
                (1.6, 2.1, "SPEAKER_01"),
                (2.1, 2.4, "SPEAKER_00"),
                (2.4, 2.9, "SPEAKER_01"),
                (2.9, 3.2, "SPEAKER_00"),
                (3.2, 3.7, "SPEAKER_01"),
                (3.7, 4.5, "SPEAKER_00"),
            ]
        )
        timestamps = [{"text": "mais comment je vais ?", "timestamp": (0.0, 4.5)}]

        aligned = SpeakerAligner().align("ignored", timestamps, diarization)

        assert [segment[0] for segment in aligned] == ["SPEAKER_01"]

    def test_the_speaker_who_talks_most_wins_though_split_across_turns(self):
        """Occupancy is what counts, not the single longest stretch."""
        diarization = build_annotation(
            [
                (0.0, 3.0, "SPEAKER_00"),
                (3.0, 5.5, "SPEAKER_01"),
                (6.0, 8.5, "SPEAKER_01"),
            ]
        )
        timestamps = [{"text": "une phrase", "timestamp": (0.0, 10.0)}]

        aligned = SpeakerAligner().align("ignored", timestamps, diarization)

        assert [segment[0] for segment in aligned] == ["SPEAKER_01"]

    def test_a_segment_nobody_speaks_over_is_dropped(self):
        """With no overlap there is no speaker to name, so nothing is emitted."""
        diarization = build_annotation([(0.0, 5.0, "SPEAKER_00")])
        timestamps = [{"text": "hors diarization", "timestamp": (20.0, 25.0)}]

        aligned = SpeakerAligner().align("ignored", timestamps, diarization)

        assert aligned == []


class TestMerging:
    """How neighbouring segments are combined once attributed."""

    def test_consecutive_segments_of_one_speaker_are_joined(self):
        """A speaker's turn is reported once, not once per transcript segment."""
        diarization = build_annotation(
            [(0.0, 10.0, "SPEAKER_00"), (10.0, 20.0, "SPEAKER_01")]
        )
        timestamps = [
            {"text": " premiere", "timestamp": (0.0, 4.0)},
            {"text": " seconde", "timestamp": (4.0, 9.0)},
            {"text": " reponse", "timestamp": (11.0, 19.0)},
        ]

        aligned = SpeakerAligner().align("ignored", timestamps, diarization)

        assert [segment[0] for segment in aligned] == ["SPEAKER_00", "SPEAKER_01"]
        assert aligned[0][3] == " premiere seconde"
