"""
Serverless handler for EchoInStone audio processing.
Can be used in containerized environments like Kubernetes pods.
"""

import json
import logging
import os
import sys
from typing import Dict, Any

# Add the parent directory to the path to import EchoInStone
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from EchoInStone.utils import configure_logging
from EchoInStone.app import EchoInStoneApp


def setup_logging():
    """Configure logging for serverless environment."""
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    configure_logging(getattr(logging, log_level))


def lambda_handler(event: Dict[str, Any], context: Any = None) -> Dict[str, Any]:
    """
    AWS Lambda handler function.
    
    Args:
        event: Lambda event containing the audio input URL
        context: Lambda context (unused)
        
    Returns:
        Dict containing the processing result
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Extract parameters from event
        echo_input = event.get('echo_input')
        output_dir = event.get('output_dir', '/tmp/results')
        
        if not echo_input:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Missing required parameter: echo_input'
                })
            }
        
        # Process audio
        app = EchoInStoneApp(output_dir=output_dir)
        result = app.process_audio_sync(echo_input)
        
        status_code = 200 if result['status'] == 'success' else 500
        
        return {
            'statusCode': status_code,
            'body': json.dumps(result)
        }
        
    except Exception as e:
        logger.error(f"Lambda handler error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': f'Internal server error: {str(e)}'
            })
        }


def kubernetes_handler(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Kubernetes pod handler function.
    
    Args:
        request_data: Dictionary containing the request parameters
        
    Returns:
        Dict containing the processing result
    """
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        echo_input = request_data.get('echo_input')
        output_dir = request_data.get('output_dir', '/app/results')
        
        if not echo_input:
            return {
                'status': 'error',
                'message': 'Missing required parameter: echo_input'
            }
        
        # Process audio
        app = EchoInStoneApp(output_dir=output_dir)
        result = app.process_audio_sync(echo_input)
        
        return result
        
    except Exception as e:
        logger.error(f"Kubernetes handler error: {str(e)}")
        return {
            'status': 'error',
            'message': f'Processing failed: {str(e)}'
        }


def http_handler():
    """
    Generic HTTP handler for web frameworks like Flask/FastAPI.
    Can be adapted for specific web framework integrations.
    """
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    setup_logging()
    
    @app.route('/process', methods=['POST'])
    def process_audio():
        try:
            data = request.get_json()
            result = kubernetes_handler(data)
            
            status_code = 200 if result['status'] == 'success' else 400
            return jsonify(result), status_code
            
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'Request processing failed: {str(e)}'
            }), 500
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy'}), 200
    
    return app


if __name__ == "__main__":
    # For testing purposes
    test_event = {
        'echo_input': 'https://www.youtube.com/watch?v=plZRCMx_Jd8',
        'output_dir': 'test_results'
    }
    
    print("Testing serverless handler...")
    result = kubernetes_handler(test_event)
    print(json.dumps(result, indent=2))