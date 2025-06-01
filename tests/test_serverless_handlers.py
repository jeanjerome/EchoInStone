import pytest
import json
import tempfile
import shutil
import os
from unittest.mock import patch, MagicMock
from serverless.handler import lambda_handler, kubernetes_handler, http_handler


class TestServerlessHandlers:
    """Integration tests for serverless deployment handlers"""
    
    def setup_method(self):
        """Setup test environment before each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.sample_event = {
            "echo_input": "https://www.youtube.com/watch?v=test",
            "output_dir": self.temp_dir
        }
        self.sample_transcriptions = [
            ("Speaker_1", 0.0, 5.0, "Test transcription")
        ]
    
    def teardown_method(self):
        """Cleanup test environment after each test"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('serverless.handler.EchoInStoneApp')
    def test_lambda_handler_success(self, mock_app_class):
        """Test AWS Lambda handler with successful processing"""
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app
        mock_app.process_audio_sync.return_value = {
            "status": "success",
            "transcriptions": self.sample_transcriptions,
            "message": "Successfully processed"
        }
        
        result = lambda_handler(self.sample_event, None)
        
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["status"] == "success"
        # JSON serialization converts tuples to lists
        expected_transcriptions = [list(t) for t in self.sample_transcriptions]
        assert body["transcriptions"] == expected_transcriptions
        
        mock_app_class.assert_called_once_with(output_dir=self.temp_dir)
        mock_app.process_audio_sync.assert_called_once_with("https://www.youtube.com/watch?v=test")
    
    @patch('serverless.handler.EchoInStoneApp')
    def test_lambda_handler_processing_error(self, mock_app_class):
        """Test Lambda handler when processing fails"""
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app
        mock_app.process_audio_sync.return_value = {
            "status": "error",
            "message": "No transcriptions were generated"
        }
        
        result = lambda_handler(self.sample_event, None)
        
        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert body["status"] == "error"
    
    def test_lambda_handler_missing_input(self):
        """Test Lambda handler with missing echo_input parameter"""
        event = {"output_dir": self.temp_dir}
        
        result = lambda_handler(event, None)
        
        assert result["statusCode"] == 400
        body = json.loads(result["body"])
        assert "Missing required parameter: echo_input" in body["error"]
    
    @patch('serverless.handler.EchoInStoneApp')
    def test_lambda_handler_exception(self, mock_app_class):
        """Test Lambda handler with unexpected exception"""
        mock_app_class.side_effect = Exception("Initialization failed")
        
        result = lambda_handler(self.sample_event, None)
        
        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert "Internal server error" in body["error"]
    
    def test_lambda_handler_default_output_dir(self):
        """Test Lambda handler uses default output directory"""
        event = {"echo_input": "https://www.youtube.com/watch?v=test"}
        
        with patch('serverless.handler.EchoInStoneApp') as mock_app_class:
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app
            mock_app.process_audio_sync.return_value = {
                "status": "success",
                "transcriptions": self.sample_transcriptions
            }
            
            lambda_handler(event, None)
            
            mock_app_class.assert_called_once_with(output_dir="/tmp/results")
    
    @patch('serverless.handler.EchoInStoneApp')
    def test_kubernetes_handler_success(self, mock_app_class):
        """Test Kubernetes pod handler with successful processing"""
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app
        mock_app.process_audio_sync.return_value = {
            "status": "success",
            "transcriptions": self.sample_transcriptions,
            "message": "Successfully processed"
        }
        
        request_data = {
            "echo_input": "https://www.youtube.com/watch?v=test",
            "output_dir": self.temp_dir
        }
        
        result = kubernetes_handler(request_data)
        
        assert result["status"] == "success"
        assert result["transcriptions"] == self.sample_transcriptions
        
        mock_app_class.assert_called_once_with(output_dir=self.temp_dir)
        mock_app.process_audio_sync.assert_called_once_with("https://www.youtube.com/watch?v=test")
    
    def test_kubernetes_handler_missing_input(self):
        """Test Kubernetes handler with missing echo_input"""
        request_data = {"output_dir": self.temp_dir}
        
        result = kubernetes_handler(request_data)
        
        assert result["status"] == "error"
        assert "Missing required parameter: echo_input" in result["message"]
    
    def test_kubernetes_handler_default_output_dir(self):
        """Test Kubernetes handler uses default output directory"""
        request_data = {"echo_input": "https://www.youtube.com/watch?v=test"}
        
        with patch('serverless.handler.EchoInStoneApp') as mock_app_class:
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app
            mock_app.process_audio_sync.return_value = {
                "status": "success",
                "transcriptions": self.sample_transcriptions
            }
            
            kubernetes_handler(request_data)
            
            mock_app_class.assert_called_once_with(output_dir="/app/results")
    
    @patch('serverless.handler.EchoInStoneApp')
    def test_kubernetes_handler_exception(self, mock_app_class):
        """Test Kubernetes handler with unexpected exception"""
        mock_app_class.side_effect = Exception("Processing failed")
        
        request_data = {"echo_input": "https://www.youtube.com/watch?v=test"}
        
        result = kubernetes_handler(request_data)
        
        assert result["status"] == "error"
        assert "Processing failed: Processing failed" in result["message"]
    
    @patch('serverless.handler.kubernetes_handler')
    def test_http_handler_process_endpoint(self, mock_k8s_handler):
        """Test HTTP API process endpoint"""
        mock_k8s_handler.return_value = {
            "status": "success",
            "transcriptions": self.sample_transcriptions
        }
        
        app = http_handler()
        client = app.test_client()
        
        response = client.post('/process', 
                             json={"echo_input": "https://www.youtube.com/watch?v=test"},
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "success"
        # HTTP API returns JSON which converts tuples to lists
        expected_transcriptions = [list(t) for t in self.sample_transcriptions]
        assert data["transcriptions"] == expected_transcriptions
    
    @patch('serverless.handler.kubernetes_handler')
    def test_http_handler_process_error(self, mock_k8s_handler):
        """Test HTTP API process endpoint with processing error"""
        mock_k8s_handler.return_value = {
            "status": "error",
            "message": "Processing failed"
        }
        
        app = http_handler()
        client = app.test_client()
        
        response = client.post('/process', 
                             json={"echo_input": "https://www.youtube.com/watch?v=test"},
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data["status"] == "error"
        assert data["message"] == "Processing failed"
    
    def test_http_handler_health_endpoint(self):
        """Test HTTP API health check endpoint"""
        app = http_handler()
        client = app.test_client()
        
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "healthy"
    
    def test_http_handler_invalid_json(self):
        """Test HTTP API with invalid JSON"""
        app = http_handler()
        client = app.test_client()
        
        response = client.post('/process', 
                             data="invalid json",
                             content_type='application/json')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data["status"] == "error"