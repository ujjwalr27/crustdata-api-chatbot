from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging
from text_processor import TextProcessor
from dotenv import load_dotenv
import os
import signal
import sys
import asyncio

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='build', static_url_path='')
CORS(app)

# Initialize text processor
text_processor = TextProcessor()

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat():
    """Handle chat requests"""
    if request.method == 'OPTIONS':
        return '', 200
        
    try:
        data = request.get_json()
        if not data:
            logger.error("No JSON data received")
            return jsonify({'error': 'No data provided'}), 400
            
        question = data.get('message')
        if not question:
            logger.error("No message in request data")
            return jsonify({'error': 'No message provided'}), 400
            
        logger.info(f"Received question: {question}")
        
        # Create event loop and run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        answer = loop.run_until_complete(text_processor.process_question(question))
        loop.close()
        
        if not answer:
            logger.error("No answer generated")
            return jsonify({'error': 'Could not generate response'}), 500
            
        logger.info("Answer generated successfully")
        return jsonify({
            'answer': answer,
            'sources': []
        })
            
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh', methods=['POST'])
def refresh_knowledge():
    """Refresh the knowledge base"""
    try:
        logger.info("Refreshing knowledge base...")
        # Reinitialize the text processor
        global text_processor
        text_processor = TextProcessor()
        
        return jsonify({
            'status': 'success',
            'message': 'Knowledge base refreshed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Error refreshing knowledge base: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to refresh knowledge base: {str(e)}'
        }), 500

@app.route('/')
def serve():
    """Serve React App"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory(app.static_folder + '/static', path)

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors by serving index.html"""
    return send_from_directory(app.static_folder, 'index.html')

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("Shutting down server...")
    sys.exit(0)

if __name__ == '__main__':
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Get port from environment or use default
        port = int(os.getenv('PORT', 5000))
        
        # Run with better server settings
        app.run(
            host='0.0.0.0',
            port=port,
            debug=True,
            use_reloader=True,
            threaded=True,
            processes=1  # Use single process for better stability
        )
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)
    finally:
        # Cleanup
        logger.info("Server stopped")