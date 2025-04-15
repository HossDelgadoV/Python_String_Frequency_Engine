# api_server.py
"""
RESTful API server for String Frequency Analyzer with visualization support
"""
import logging
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import base64
import io
from string_analyzer.analyzer import StringAnalyzer
from string_analyzer.visualizer import StringVisualizer

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

@app.route('/visualize/<viz_type>', methods=['POST'])
def visualize_text(viz_type):
    """Generate visualizations for analyzed text"""
    try:
        # Get request data
        request_data = request.get_json()
        
        if not request_data or 'text' not in request_data:
            return jsonify({
                'error': 'No text provided for visualization'
            }), 400
            
        input_text = request_data['text']
        
        # Analyze the text first
        analyzer = StringAnalyzer(input_text)
        results = analyzer.analyze()
        
        # Add the original text to results for character distribution analysis
        results['text'] = input_text
        
        # Create visualizer
        visualizer = StringVisualizer(results)
        
        # Generate the requested visualization
        base64_image = None
        
        if viz_type == 'char_freq':
            base64_image = visualizer.create_character_frequency_chart(return_base64=True)
        elif viz_type == 'word_freq':
            max_words = request_data.get('max_words', 15)
            base64_image = visualizer.create_word_frequency_chart(max_words=max_words, return_base64=True)
        elif viz_type == 'word_cloud':
            base64_image = visualizer.create_word_cloud(return_base64=True)
        elif viz_type == 'char_dist':
            base64_image = visualizer.create_distribution_chart(return_base64=True)
        elif viz_type == 'all':
            # Generate all visualizations
            all_viz = {}
            
            char_freq = visualizer.create_character_frequency_chart(return_base64=True)
            if char_freq:
                all_viz['char_freq'] = char_freq
                
            word_freq = visualizer.create_word_frequency_chart(return_base64=True)
            if word_freq:
                all_viz['word_freq'] = word_freq
                
            word_cloud = visualizer.create_word_cloud(return_base64=True)
            if word_cloud:
                all_viz['word_cloud'] = word_cloud
                
            char_dist = visualizer.create_distribution_chart(return_base64=True)
            if char_dist:
                all_viz['char_dist'] = char_dist
                
            return jsonify({
                'visualizations': all_viz,
                'format': 'base64'
            })
        else:
            return jsonify({
                'error': f'Unknown visualization type: {viz_type}'
            }), 400
            
        if base64_image:
            return jsonify({
                'image': base64_image,
                'format': 'base64'
            })
        else:
            return jsonify({
                'error': 'Failed to generate visualization'
            }), 500
            
    except Exception as e:
        logger.error(f"Error generating visualization: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/analyze_file', methods=['POST'])
def analyze_file():
    """Analyze uploaded file"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'error': 'No file uploaded'
            }), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'error': 'Empty file name'
            }), 400
            
        # Read file content
        file_content = file.read().decode('utf-8')
        
        # Create analyzer and analyze
        analyzer = StringAnalyzer(file_content)
        results = analyzer.analyze()
        
        # Format results
        formatted_results = analyzer.format_results()
        
        return jsonify({
            'results': formatted_results,
            'format': 'text'
        })
        
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'string-frequency-analyzer-api',
        'features': ['text_analysis', 'visualizations', 'file_processing']
    })

if __name__ == '__main__':
    logger.info("Starting String Frequency Analyzer API server...")
    app.run(host='127.0.0.1', port=5000, debug=True)