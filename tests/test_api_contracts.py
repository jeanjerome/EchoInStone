import pytest
import json
from unittest.mock import patch, MagicMock
from serverless.handler import lambda_handler, kubernetes_handler


class TestAPIContracts:
    """Tests to ensure API contracts are maintained across serverless deployments"""
    
    def setup_method(self):
        """Setup test data"""
        self.sample_transcriptions = [
            ("Speaker_1", 0.0, 5.0, "Test transcription"),
            ("Speaker_2", 5.0, 10.0, "Another transcription")
        ]
        self.valid_request = {
            "echo_input": "https://www.youtube.com/watch?v=test",
            "output_dir": "/tmp/test"
        }
    
    def test_success_response_contract(self):
        """Test that all handlers return consistent success response format"""
        expected_fields = ["status", "transcriptions", "output_file", "message"]
        
        with patch('serverless.handler.EchoInStoneApp') as mock_app_class:
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app
            mock_app.process_audio_sync.return_value = {
                "status": "success",
                "transcriptions": self.sample_transcriptions,
                "output_file": "speaker_transcriptions.json",
                "message": "Successfully processed audio with 2 segments"
            }
            
            # Test Lambda handler
            lambda_response = lambda_handler(self.valid_request, None)
            assert lambda_response["statusCode"] == 200
            lambda_body = json.loads(lambda_response["body"])
            
            # Test Kubernetes handler
            k8s_response = kubernetes_handler(self.valid_request)
            
            # Both should have same structure
            for field in expected_fields:
                assert field in lambda_body
                assert field in k8s_response
            
            # Both should have same values
            assert lambda_body["status"] == k8s_response["status"] == "success"
            # Lambda converts tuples to lists via JSON, so compare normalized versions
            lambda_transcriptions = [list(t) if isinstance(t, (tuple, list)) else t for t in lambda_body["transcriptions"]]
            k8s_transcriptions = [list(t) if isinstance(t, (tuple, list)) else t for t in k8s_response["transcriptions"]]
            assert lambda_transcriptions == k8s_transcriptions
    
    def test_error_response_contract(self):
        """Test that all handlers return consistent error response format"""
        expected_fields = ["status", "message"]
        
        with patch('serverless.handler.EchoInStoneApp') as mock_app_class:
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app
            mock_app.process_audio_sync.return_value = {
                "status": "error",
                "message": "No transcriptions were generated"
            }
            
            # Test Lambda handler
            lambda_response = lambda_handler(self.valid_request, None)
            assert lambda_response["statusCode"] == 500
            lambda_body = json.loads(lambda_response["body"])
            
            # Test Kubernetes handler
            k8s_response = kubernetes_handler(self.valid_request)
            
            # Both should have same structure
            for field in expected_fields:
                assert field in lambda_body
                assert field in k8s_response
            
            # Both should have same values
            assert lambda_body["status"] == k8s_response["status"] == "error"
            assert lambda_body["message"] == k8s_response["message"]
    
    def test_transcription_data_format(self):
        """Test that transcription data format is consistent"""
        with patch('serverless.handler.EchoInStoneApp') as mock_app_class:
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app
            mock_app.process_audio_sync.return_value = {
                "status": "success",
                "transcriptions": self.sample_transcriptions,
                "output_file": "test.json",
                "message": "Success"
            }
            
            # Test both handlers
            lambda_response = lambda_handler(self.valid_request, None)
            lambda_body = json.loads(lambda_response["body"])
            
            k8s_response = kubernetes_handler(self.valid_request)
            
            # Validate transcription format
            for i, response in enumerate([lambda_body, k8s_response]):
                response_name = ["Lambda", "Kubernetes"][i]
                assert isinstance(response["transcriptions"], list), f"{response_name} transcriptions should be a list"
                for transcription in response["transcriptions"]:
                    # Lambda converts tuples to lists, Kubernetes keeps tuples
                    assert isinstance(transcription, (list, tuple)), f"{response_name} transcription should be list or tuple"
                    assert len(transcription) == 4  # speaker, start, end, text
                    assert isinstance(transcription[0], str)  # speaker
                    assert isinstance(transcription[1], (int, float))  # start time
                    assert isinstance(transcription[2], (int, float))  # end time
                    assert isinstance(transcription[3], str)  # text
    
    def test_http_status_code_mapping(self):
        """Test that Lambda handler maps internal status to correct HTTP codes"""
        test_cases = [
            ({"status": "success", "transcriptions": []}, 200),
            ({"status": "error", "message": "Processing failed"}, 500)
        ]
        
        for mock_result, expected_status_code in test_cases:
            with patch('serverless.handler.EchoInStoneApp') as mock_app_class:
                mock_app = MagicMock()
                mock_app_class.return_value = mock_app
                mock_app.process_audio_sync.return_value = mock_result
                
                response = lambda_handler(self.valid_request, None)
                assert response["statusCode"] == expected_status_code
    
    def test_required_parameters_validation(self):
        """Test that missing required parameters are handled consistently"""
        invalid_request = {"output_dir": "/tmp/test"}  # Missing echo_input
        
        # Test Lambda handler
        lambda_response = lambda_handler(invalid_request, None)
        assert lambda_response["statusCode"] == 400
        lambda_body = json.loads(lambda_response["body"])
        assert "error" in lambda_body
        assert "echo_input" in lambda_body["error"]
        
        # Test Kubernetes handler
        k8s_response = kubernetes_handler(invalid_request)
        assert k8s_response["status"] == "error"
        assert "echo_input" in k8s_response["message"]
    
    def test_exception_handling_consistency(self):
        """Test that exceptions are handled consistently across handlers"""
        with patch('serverless.handler.EchoInStoneApp') as mock_app_class:
            mock_app_class.side_effect = Exception("Test exception")
            
            # Test Lambda handler
            lambda_response = lambda_handler(self.valid_request, None)
            assert lambda_response["statusCode"] == 500
            lambda_body = json.loads(lambda_response["body"])
            assert "error" in lambda_body
            assert "Test exception" in lambda_body["error"]
            
            # Test Kubernetes handler
            k8s_response = kubernetes_handler(self.valid_request)
            assert k8s_response["status"] == "error"
            assert "Test exception" in k8s_response["message"]
    
    def test_default_output_directory_behavior(self):
        """Test that default output directories are set correctly for each deployment"""
        request_without_output_dir = {"echo_input": "https://test.com"}
        
        with patch('serverless.handler.EchoInStoneApp') as mock_app_class:
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app
            mock_app.process_audio_sync.return_value = {
                "status": "success",
                "transcriptions": []
            }
            
            # Test Lambda handler default
            lambda_handler(request_without_output_dir, None)
            lambda_call_args = mock_app_class.call_args
            assert lambda_call_args[1]["output_dir"] == "/tmp/results"
            
            # Reset mock
            mock_app_class.reset_mock()
            
            # Test Kubernetes handler default
            kubernetes_handler(request_without_output_dir)
            k8s_call_args = mock_app_class.call_args
            assert k8s_call_args[1]["output_dir"] == "/app/results"
    
    def test_response_serialization(self):
        """Test that all responses can be properly serialized to JSON"""
        with patch('serverless.handler.EchoInStoneApp') as mock_app_class:
            mock_app = MagicMock()
            mock_app_class.return_value = mock_app
            mock_app.process_audio_sync.return_value = {
                "status": "success",
                "transcriptions": self.sample_transcriptions,
                "output_file": "test.json",
                "message": "Success"
            }
            
            # Test Lambda response serialization
            lambda_response = lambda_handler(self.valid_request, None)
            lambda_body_str = lambda_response["body"]
            lambda_body = json.loads(lambda_body_str)  # Should not raise exception
            
            # Test Kubernetes response serialization
            k8s_response = kubernetes_handler(self.valid_request)
            json.dumps(k8s_response)  # Should not raise exception
            
            # Verify both can be round-tripped through JSON
            assert json.loads(json.dumps(lambda_body)) == lambda_body
            # For Kubernetes response, tuples become lists after JSON round-trip
            k8s_json_roundtrip = json.loads(json.dumps(k8s_response))
            # Normalize both for comparison by converting tuples to lists
            def normalize_transcriptions(response):
                if "transcriptions" in response:
                    response["transcriptions"] = [list(t) for t in response["transcriptions"]]
                return response
            assert normalize_transcriptions(k8s_json_roundtrip.copy()) == normalize_transcriptions(k8s_response.copy())