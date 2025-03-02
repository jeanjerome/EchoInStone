from EchoInStone.processing.aligner_interface import AlignerInterface
import logging
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

class SpeakerAligner(AlignerInterface):
    def __init__(self, overlap_threshold=0.5, min_segment_duration=1.0):
        """Initialize the SpeakerAligner with configurable parameters.

        Args:
            overlap_threshold (float): Minimum overlap ratio to consider a match (0.0-1.0)
            min_segment_duration (float): Minimum duration in seconds for merged segments
        """
        self.overlap_threshold = overlap_threshold
        self.min_segment_duration = min_segment_duration

    def align(self, transcription, timestamps, diarization):
        """Aligns transcription with timestamps and speaker diarization.

        Args:
            transcription (str): The complete text of the transcription.
            timestamps (list): List of text segments with timestamps.
            diarization (object): Diarization object containing speaker segments.

        Returns:
            list: List of aligned segments with speaker identifiers and timestamps.
        """
        logger.debug("Combining transcription and diarization...")
        
        if not timestamps or diarization is None:
            logger.warning("Missing timestamps or diarization data")
            return []
            
        # Pre-process diarization data for faster lookups
        diarization_map = self._build_diarization_map(diarization)
        
        # Process timestamps with efficient speaker assignment
        speaker_transcriptions = self._assign_speakers(timestamps, diarization_map, diarization)
        
        # Merge consecutive segments of the same speaker
        merged_segments = self._merge_consecutive_segments(speaker_transcriptions)
        
        return merged_segments

    def _build_diarization_map(self, diarization):
        """Build a time-indexed map of speaker segments for efficient lookup.
        
        Args:
            diarization (object): Diarization object containing speaker segments.
            
        Returns:
            dict: Dictionary mapping time points to speaker segments
        """
        diarization_map = defaultdict(list)
        
        # Extract all speaker segments and organize them by time
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            start_time = turn.start
            end_time = turn.end
            diarization_map[(start_time, end_time)].append(speaker)
            
        return diarization_map

    def _assign_speakers(self, timestamps, diarization_map, diarization):
        """Assign speakers to transcription segments efficiently.
        
        Args:
            timestamps (list): List of text segments with timestamps.
            diarization_map (dict): Pre-processed diarization mapping.
            diarization (object): Original diarization object.
            
        Returns:
            list: List of segments with assigned speakers.
        """
        speaker_transcriptions = []
        
        # Find end of audio
        last_diarization_end = self._get_last_segment_time(diarization)
        
        # Process each transcription chunk
        for chunk in timestamps:
            # Extract timestamp information
            if len(chunk.get('timestamp')) >= 2:
                chunk_start = chunk['timestamp'][0]
                chunk_end = chunk['timestamp'][1] if chunk['timestamp'][1] is not None else last_diarization_end
            else:
                # Handle cases with missing timestamps
                continue
            
            segment_text = chunk.get('text', '').strip()
            if not segment_text:
                continue
            
            # Find best speaker using the vectorized algorithm
            speaker = self._find_dominant_speaker(chunk_start, chunk_end, diarization)
            if speaker:
                speaker_transcriptions.append((speaker, chunk_start, chunk_end, segment_text))
        
        return speaker_transcriptions

    def _find_dominant_speaker(self, start_time, end_time, diarization):
        """Find the dominant speaker for a given time segment.
        
        Args:
            start_time (float): Start time of segment.
            end_time (float): End time of segment.
            diarization (object): Diarization object.
            
        Returns:
            str: The dominant speaker label or None.
        """
        speaker_durations = defaultdict(float)
        segment_duration = end_time - start_time
        
        # Calculate overlap with each speaker segment
        for turn, _, speaker in diarization.itertracks(yield_label=True):
            # Calculate intersection
            intersection_start = max(start_time, turn.start)
            intersection_end = min(end_time, turn.end)
            
            if intersection_end > intersection_start:
                overlap_duration = intersection_end - intersection_start
                speaker_durations[speaker] += overlap_duration
        
        # Find dominant speaker (most talking time)
        if not speaker_durations:
            return None
            
        dominant_speaker = max(speaker_durations.items(), key=lambda x: x[1])
        
        # Check if dominant speaker meets threshold
        if dominant_speaker[1] / segment_duration >= self.overlap_threshold:
            return dominant_speaker[0]
            
        return None

    def _merge_consecutive_segments(self, segments):
        """Merges consecutive segments of the same speaker with improved algorithm.

        Args:
            segments (list): List of segments to merge.

        Returns:
            list: List of merged segments.
        """
        if not segments:
            return []
            
        merged_segments = []
        current_group = list(segments[0])  # Convert to list for easier modification
        
        for segment in segments[1:]:
            if (segment[0] == current_group[0] and 
                abs(segment[1] - current_group[2]) < 0.5):  # Time gap tolerance
                
                # Update end time and concatenate text
                current_group[2] = segment[2]
                current_group[3] += " " + segment[3]
            else:
                # Start new segment if different speaker or significant time gap
                merged_segments.append(tuple(current_group))
                current_group = list(segment)
        
        # Add the last group
        if current_group:
            merged_segments.append(tuple(current_group))
        
        return merged_segments

    def _get_last_segment_time(self, annotation):
        """Get the end time of the last segment, optimized version.

        Args:
            annotation (object): Annotation object containing segments.

        Returns:
            float: The end time of the last segment.
        """
        last_time = 0.0
        
        for segment in annotation.itersegments():
            if segment.end > last_time:
                last_time = segment.end
                
        return last_time