import pytest
import tempfile
import shutil
import os
from unittest.mock import patch, MagicMock
from EchoInStone.app import EchoInStoneApp


class TestEchoInStoneApp:
    """Unit tests for EchoInStoneApp class - the new serverless-ready application layer"""
    
    def setup_method(self):
        """Setup test environment before each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.app = EchoInStoneApp(output_dir=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment after each test"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_app_initialization(self):
        """Test EchoInStoneApp initialization with lazy loading"""
        assert self.app.output_dir == self.temp_dir
        assert self.app._transcriber is None
        assert self.app._diarizer is None
        assert self.app._aligner is None
        assert self.app._data_saver is None
    
    @patch('EchoInStone.app.WhisperAudioTranscriber')
    @patch('EchoInStone.app.PyannoteDiarizer')
    @patch('EchoInStone.app.SpeakerAligner')
    @patch('EchoInStone.app.DataSaver')
    def test_lazy_component_initialization(self, mock_data_saver, mock_aligner, mock_diarizer, mock_transcriber):
        """Test that components are initialized only when needed"""
        self.app._initialize_components()
        
        mock_transcriber.assert_called_once()
        mock_diarizer.assert_called_once()
        mock_aligner.assert_called_once()
        mock_data_saver.assert_called_once_with(output_dir=self.temp_dir)
        
        assert self.app._transcriber is not None
        assert self.app._diarizer is not None
        assert self.app._aligner is not None
        assert self.app._data_saver is not None
    
    @patch('EchoInStone.app.get_downloader')
    @patch('EchoInStone.app.AudioProcessingOrchestrator')
    def test_process_audio_success(self, mock_orchestrator, mock_get_downloader):
        """Test successful audio processing flow"""
        mock_downloader = MagicMock()
        mock_get_downloader.return_value = mock_downloader
        
        mock_transcriptions = [
            ("Speaker_1", 0.0, 5.0, "Test transcription 1"),
            ("Speaker_2", 5.0, 10.0, "Test transcription 2")
        ]
        mock_orchestrator_instance = MagicMock()
        mock_orchestrator_instance.extract_and_transcribe.return_value = mock_transcriptions
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Mock the data_saver properly
        mock_data_saver = MagicMock()
        with patch.object(self.app, '_initialize_components') as mock_init:
            def init_components():
                self.app._data_saver = mock_data_saver
            mock_init.side_effect = init_components
            
            result = self.app.process_audio("test_url", "output.json")
        
        assert result == mock_transcriptions
        mock_get_downloader.assert_called_once_with("test_url", self.temp_dir)
        mock_orchestrator_instance.extract_and_transcribe.assert_called_once_with("test_url")
        mock_data_saver.save_data.assert_called_once_with("output.json", mock_transcriptions)
    
    @patch('EchoInStone.app.get_downloader')
    @patch('EchoInStone.app.AudioProcessingOrchestrator')
    def test_process_audio_failure(self, mock_orchestrator, mock_get_downloader):
        """Test audio processing when no transcriptions are generated"""
        mock_downloader = MagicMock()
        mock_get_downloader.return_value = mock_downloader
        
        mock_orchestrator_instance = MagicMock()
        mock_orchestrator_instance.extract_and_transcribe.return_value = None
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        with patch.object(self.app, '_initialize_components'):
            result = self.app.process_audio("test_url", "output.json")
        
        assert result is None
    
    @patch('EchoInStone.app.get_downloader')
    @patch('EchoInStone.app.AudioProcessingOrchestrator')
    def test_process_audio_sync_success(self, mock_orchestrator, mock_get_downloader):
        """Test synchronous processing for serverless environments"""
        mock_downloader = MagicMock()
        mock_get_downloader.return_value = mock_downloader
        
        mock_transcriptions = [
            ("Speaker_1", 0.0, 5.0, "Test transcription 1")
        ]
        mock_orchestrator_instance = MagicMock()
        mock_orchestrator_instance.extract_and_transcribe.return_value = mock_transcriptions
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        # Mock the data_saver properly
        mock_data_saver = MagicMock()
        with patch.object(self.app, '_initialize_components') as mock_init:
            def init_components():
                self.app._data_saver = mock_data_saver
            mock_init.side_effect = init_components
            
            result = self.app.process_audio_sync("test_url")
        
        assert result["status"] == "success"
        assert result["transcriptions"] == mock_transcriptions
        assert "Successfully processed audio with 1 segments" in result["message"]
        assert result["output_file"] == "speaker_transcriptions.json"
    
    @patch('EchoInStone.app.get_downloader')
    @patch('EchoInStone.app.AudioProcessingOrchestrator')
    def test_process_audio_sync_no_transcriptions(self, mock_orchestrator, mock_get_downloader):
        """Test sync processing when no transcriptions are generated"""
        mock_downloader = MagicMock()
        mock_get_downloader.return_value = mock_downloader
        
        mock_orchestrator_instance = MagicMock()
        mock_orchestrator_instance.extract_and_transcribe.return_value = None
        mock_orchestrator.return_value = mock_orchestrator_instance
        
        with patch.object(self.app, '_initialize_components'):
            result = self.app.process_audio_sync("test_url")
        
        assert result["status"] == "error"
        assert result["message"] == "No transcriptions were generated"
    
    @patch('EchoInStone.app.get_downloader')
    def test_process_audio_sync_exception_handling(self, mock_get_downloader):
        """Test that exceptions are properly caught and returned as error responses"""
        mock_get_downloader.side_effect = Exception("Network timeout")
        
        result = self.app.process_audio_sync("test_url")
        
        assert result["status"] == "error"
        assert "Processing failed: Network timeout" in result["message"]
    
    def test_app_default_output_dir(self):
        """Test default output directory initialization"""
        app = EchoInStoneApp()
        assert app.output_dir == "results"