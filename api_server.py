# api_server.py
"""
RESTful API server for String Frequency Analyzer
"""
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from string_analyzer.analyzer import StringAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("StringAnalyzer.API")

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

@app.route('/analyze', methods=['POST'])
def analyze_text():
    """Analyze text provided in request body"""
    try:
        # Get request data
        request_data = request.get_json()
        
        if not request_data or 'text' not in request_data:
            return jsonify({
                'error': 'No text provided for analysis'
            }), 400
            
        input_text = request_data['text']
        
        # Log request (truncate long text for logging)
        text_preview = input_text[:50] + "..." if len(input_text) > 50 else input_text
        logger.info(f"Analyzing text: {text_preview}")
        
        # Create analyzer and analyze
        analyzer = StringAnalyzer(input_text)
        results = analyzer.analyze()
        
        # Format results based on requested format
        output_format = request_data.get('format', 'text')
        
        if output_format == 'text':
            formatted_results = analyzer.format_results()
            return jsonify({
                'results': formatted_results,
                'format': 'text'
            })
        else:
            # Return raw JSON results
            return jsonify({
                'results': results,
                'format': 'json'
            })
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'string-frequency-analyzer-api'
    })

if __name__ == '__main__':
    logger.info("Starting String Frequency Analyzer API server...")
    app.run(host='127.0.0.1', port=5000, debug=True)