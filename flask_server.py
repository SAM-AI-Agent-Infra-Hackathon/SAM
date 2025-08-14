#!/usr/bin/env python3
"""
Flask Backend for Modern Chat UI
================================

Serves the HTML chat interface and provides API endpoints for the immigration agent.
"""

import os
import sys
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Ensure src is importable
BASE_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(BASE_DIR, 'src'))

from immigration_main_agent import EnhancedImmigrationAgent

# Load environment
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

# Initialize agent
agent = EnhancedImmigrationAgent()

@app.route('/')
def serve_chat():
    """Serve the main chat interface"""
    return send_from_directory('.', 'chat_ui.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from the frontend"""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Process with immigration agent
        if message.strip().lower().startswith("/profile "):
            company = message.strip()[9:].strip()
            if not company:
                response = "Please provide a company name, e.g., /profile Google"
            else:
                response = agent.get_company_profile(company)
        else:
            response = agent.process_query(message)
        
        return jsonify({'response': response})
        
    except Exception as e:
        print(f"Error processing chat: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)
