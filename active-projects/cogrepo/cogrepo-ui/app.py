#!/usr/bin/env python3
"""
CogRepo Web Server with Upload & Real-time Processing

Features:
- File upload with drag-and-drop support
- Real-time progress via WebSocket
- Import history and statistics
- Search and browse conversations
- Mobile-responsive modern UI
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path
import json
import os
import sys
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional
import uuid

# Load environment variables
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / '.env')

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from models import ProcessingStats
from parsers import ChatGPTParser, ClaudeParser, GeminiParser
from state_manager import ProcessingStateManager
from enrichment import EnrichmentPipeline
from cogrepo_import import CogRepoImporter
import yaml

# Initialize Flask app
app = Flask(__name__, static_folder='static', template_folder='.')
app.config['SECRET_KEY'] = os.urandom(24)
app.config['UPLOAD_FOLDER'] = Path(__file__).parent / 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size

# Ensure upload directory exists
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)

# Initialize SocketIO for real-time updates
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
CORS(app)

# Global state for tracking active imports
active_imports: Dict[str, Dict[str, Any]] = {}
import_lock = threading.Lock()


def get_repo_path():
    """Get the repository data path"""
    possible_paths = [
        Path(__file__).parent.parent / "data" / "enriched_repository.jsonl",
        Path(__file__).parent / "../data/enriched_repository.jsonl",
    ]

    for path in possible_paths:
        if path.exists():
            return str(path)

    return str(possible_paths[0])


class ProgressCallback:
    """Callback class for tracking import progress"""

    def __init__(self, import_id: str, socketio_instance):
        self.import_id = import_id
        self.socketio = socketio_instance
        self.current = 0
        self.total = 0
        self.status = "initializing"
        self.message = ""

    def update(self, current: int, total: int, status: str, message: str = ""):
        """Update progress and emit to WebSocket"""
        self.current = current
        self.total = total
        self.status = status
        self.message = message

        self.socketio.emit('import_progress', {
            'import_id': self.import_id,
            'current': current,
            'total': total,
            'percentage': int((current / total * 100) if total > 0 else 0),
            'status': status,
            'message': message
        })


def process_import_background(
    import_id: str,
    file_path: str,
    source: str,
    enrich: bool,
    config_path: str
):
    """Background thread for processing imports"""
    try:
        # Update status
        with import_lock:
            active_imports[import_id]['status'] = 'processing'
            active_imports[import_id]['start_time'] = datetime.now().isoformat()

        socketio.emit('import_status', {
            'import_id': import_id,
            'status': 'processing',
            'message': 'Starting import...'
        })

        # Create importer
        importer = CogRepoImporter(config_file=config_path)

        # Simulate progress updates (in real implementation, modify CogRepoImporter to accept callback)
        # For now, we'll use a simplified version

        socketio.emit('import_progress', {
            'import_id': import_id,
            'current': 0,
            'total': 100,
            'percentage': 0,
            'status': 'parsing',
            'message': 'Parsing export file...'
        })

        # Run the actual import
        stats = importer.import_conversations(
            file_path=file_path,
            source=source,
            enrich=enrich,
            dry_run=False
        )

        # Import completed
        with import_lock:
            active_imports[import_id]['status'] = 'completed'
            active_imports[import_id]['end_time'] = datetime.now().isoformat()
            active_imports[import_id]['stats'] = stats.to_dict()

        socketio.emit('import_complete', {
            'import_id': import_id,
            'status': 'completed',
            'stats': stats.to_dict(),
            'message': f'Successfully processed {stats.total_processed} conversations'
        })

    except Exception as e:
        # Import failed
        error_message = str(e)

        with import_lock:
            active_imports[import_id]['status'] = 'failed'
            active_imports[import_id]['end_time'] = datetime.now().isoformat()
            active_imports[import_id]['error'] = error_message

        socketio.emit('import_error', {
            'import_id': import_id,
            'status': 'failed',
            'error': error_message,
            'message': f'Import failed: {error_message}'
        })

    finally:
        # Clean up uploaded file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass


# API Routes

@app.route('/')
def index():
    """Serve the main UI"""
    return send_from_directory('.', 'index.html')


@app.route('/api/status')
def api_status():
    """Get server status and statistics"""
    try:
        state_manager = ProcessingStateManager()
        stats = state_manager.get_stats()

        # Check if data file exists
        repo_path = get_repo_path()
        data_exists = os.path.exists(repo_path)

        if data_exists:
            # Count conversations
            with open(repo_path, 'r') as f:
                conversation_count = sum(1 for _ in f)
        else:
            conversation_count = 0

        return jsonify({
            'status': 'online',
            'data_exists': data_exists,
            'total_conversations': conversation_count,
            'stats': stats,
            'api_key_configured': bool(os.getenv('ANTHROPIC_API_KEY'))
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/upload', methods=['POST'])
def api_upload():
    """Handle file upload and start processing"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Get options
        source = request.form.get('source', 'auto')
        enrich = request.form.get('enrich', 'true').lower() == 'true'

        # Validate source
        if source not in ['auto', 'chatgpt', 'claude', 'gemini']:
            return jsonify({'error': 'Invalid source'}), 400

        # Check API key if enriching
        if enrich and not os.getenv('ANTHROPIC_API_KEY'):
            return jsonify({
                'error': 'ANTHROPIC_API_KEY not configured. Cannot enrich without API key.'
            }), 400

        # Save uploaded file
        filename = secure_filename(file.filename)
        import_id = str(uuid.uuid4())
        file_path = app.config['UPLOAD_FOLDER'] / f"{import_id}_{filename}"
        file.save(str(file_path))

        # Create import record
        with import_lock:
            active_imports[import_id] = {
                'id': import_id,
                'filename': filename,
                'source': source,
                'enrich': enrich,
                'status': 'queued',
                'created_time': datetime.now().isoformat(),
                'start_time': None,
                'end_time': None,
                'stats': None,
                'error': None
            }

        # Start background processing
        config_path = str(Path(__file__).parent.parent / 'config' / 'enrichment_config.yaml')

        thread = threading.Thread(
            target=process_import_background,
            args=(import_id, str(file_path), source, enrich, config_path),
            daemon=True
        )
        thread.start()

        return jsonify({
            'import_id': import_id,
            'status': 'queued',
            'message': 'Import queued for processing'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/imports')
def api_imports():
    """Get list of all imports"""
    with import_lock:
        imports_list = list(active_imports.values())

    # Sort by creation time (newest first)
    imports_list.sort(key=lambda x: x['created_time'], reverse=True)

    return jsonify({'imports': imports_list})


@app.route('/api/imports/<import_id>')
def api_import_status(import_id):
    """Get status of specific import"""
    with import_lock:
        import_data = active_imports.get(import_id)

    if not import_data:
        return jsonify({'error': 'Import not found'}), 404

    return jsonify(import_data)


@app.route('/api/conversations')
def api_conversations():
    """Get all conversations (for search UI)"""
    try:
        repo_path = get_repo_path()

        if not os.path.exists(repo_path):
            return jsonify({
                'conversations': [],
                'total': 0,
                'message': 'No conversations found. Upload some exports to get started!'
            })

        conversations = []
        with open(repo_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        conv = json.loads(line)
                        conversations.append(conv)
                    except:
                        continue

        # Apply filters if provided
        query = request.args.get('q', '').lower()
        source_filter = request.args.get('source', '')

        if query:
            conversations = [
                c for c in conversations
                if query in c.get('generated_title', '').lower()
                or query in c.get('raw_text', '').lower()
                or query in str(c.get('tags', [])).lower()
            ]

        if source_filter:
            conversations = [c for c in conversations if c.get('source', '') == source_filter]

        # Sort by timestamp (newest first)
        conversations.sort(
            key=lambda x: x.get('timestamp', ''),
            reverse=True
        )

        # Limit results
        limit = int(request.args.get('limit', 100))
        conversations = conversations[:limit]

        return jsonify({
            'conversations': conversations,
            'total': len(conversations)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# WebSocket Events

@socketio.on('connect')
def handle_connect():
    """Client connected"""
    print(f"Client connected: {request.sid}")
    emit('connected', {'message': 'Connected to CogRepo server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    print(f"Client disconnected: {request.sid}")


@socketio.on('subscribe_import')
def handle_subscribe(data):
    """Subscribe to updates for specific import"""
    import_id = data.get('import_id')
    print(f"Client {request.sid} subscribed to import {import_id}")


# Main

if __name__ == '__main__':
    print("=" * 60)
    print("  CogRepo Web Server")
    print("=" * 60)
    print(f"  📁 Data path: {get_repo_path()}")
    print(f"  📤 Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"  🔑 API key configured: {bool(os.getenv('ANTHROPIC_API_KEY'))}")
    print(f"  🌐 Starting server on http://localhost:5000")
    print("=" * 60)
    print()

    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
