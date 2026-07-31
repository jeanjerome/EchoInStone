from .aligner_interface import AlignerInterface
import logging

logger = logging.getLogger(__name__)

class SpeakerAligner(AlignerInterface):
    def align(self, transcription, timestamps, diarization):
        """Aligns the transcription with timestamps and speaker diarization.

        Args:
            transcription (str): The complete text of the transcription.
            timestamps (list): List of text segments with their corresponding timestamps.
            diarization (object): Diarization object containing speaker segments.

        Returns:
            list: List of aligned segments with speaker identifiers and timestamps.
        """
        logger.debug("Combining transcription and diarization...")
        speaker_transcriptions = []

        # Find the end time of the last segment in diarization
        last_diarization_end = self.get_last_segment(diarization).end

        for chunk in timestamps:
            chunk_start = chunk['timestamp'][0]
            chunk_end = chunk['timestamp'][1]
            segment_text = chunk['text']

            # Handle the case where chunk_end is None
            if chunk_end is None:
                # Use the end of the last diarization segment as the default end time
                chunk_end = last_diarization_end if last_diarization_end is not None else chunk_start

            # Attribute the segment to whoever holds the floor across it
            speaker = self.find_dominant_speaker(diarization, chunk_start, chunk_end)
            if speaker is not None:
                speaker_transcriptions.append((speaker, chunk_start, chunk_end, segment_text))

        # Merge consecutive segments of the same speaker
        speaker_transcriptions = self.merge_consecutive_segments(speaker_transcriptions)
        return speaker_transcriptions

    def find_dominant_speaker(self, diarization, start_time, end_time):
        """Finds the speaker holding the floor across a given time range.

        Speech is summed per speaker rather than compared turn by turn. A
        finely segmented diarization splits one speaker's answer into many
        turns and threads brief interjections from the other through it;
        comparing single turns then lets a fraction of a second carry off a
        whole transcript segment, cutting a sentence in half and crediting it
        to the wrong person. Summing keeps the segment with whoever actually
        speaks across it.

        Args:
            diarization (object): Diarization object containing speaker segments.
            start_time (float): Start time of the segment.
            end_time (float): End time of the segment.

        Returns:
            str: Label of the dominant speaker, or None when no turn overlaps.
        """
        speech_time = {}

        for turn, _, speaker in diarization.itertracks(yield_label=True):
            overlap_start = max(start_time, turn.start)
            overlap_end = min(end_time, turn.end)

            if overlap_start < overlap_end:
                speech_time[speaker] = (
                    speech_time.get(speaker, 0.0) + overlap_end - overlap_start
                )

        if not speech_time:
            return None

        return max(speech_time, key=speech_time.get)

    def merge_consecutive_segments(self, segments):
        """Merges consecutive segments of the same speaker.

        Args:
            segments (list): List of segments to merge.

        Returns:
            list: List of merged segments.
        """
        merged_segments = []
        previous_segment = None

        for segment in segments:
            if previous_segment is None:
                previous_segment = segment
            else:
                if segment[0] == previous_segment[0]:
                    # Merge segments of the same speaker that are consecutive
                    previous_segment = (
                        previous_segment[0],
                        previous_segment[1],
                        segment[2],
                        previous_segment[3] + segment[3]
                    )
                else:
                    merged_segments.append(previous_segment)
                    previous_segment = segment

        if previous_segment:
            merged_segments.append(previous_segment)

        return merged_segments

    def get_last_segment(self, annotation):
        """Retrieves the last segment from the annotation.

        Args:
            annotation (object): Annotation object containing segments.

        Returns:
            object: The last segment in the annotation.
        """
        last_segment = None
        for segment in annotation.itersegments():
            last_segment = segment
        return last_segment
