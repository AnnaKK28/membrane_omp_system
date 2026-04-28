"""
Flask backend for Membrane OMP System.
"""
import os
import sys

# Ensure the backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request
from database import init_db
from routes import solute_bp, membrane_bp, predict_bp

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')

# Register blueprints
app.register_blueprint(solute_bp)
app.register_blueprint(membrane_bp)
app.register_blueprint(predict_bp)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'service': 'Membrane OMP System API'})


@app.route('/', methods=['GET'])
def serve_frontend():
    """Serve the Vue frontend."""
    return app.send_static_file('index.html')


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    if request.path.startswith('/api/'):
        return jsonify({'success': False, 'error': 'API endpoint not found'}), 404
    return app.send_static_file('index.html')


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


def main():
    import os
    
    # Use /tmp for Railway (stateless container)
    data_dir = os.environ.get('DATA_DIR', '/tmp')
    os.makedirs(data_dir, exist_ok=True)
    
    # Initialize database on startup
    print("Initializing database...")
    init_db()

    # Import and run data import (only if DB is empty)
    print("Loading data from Excel...")
    try:
        from database import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM solute")
        count = cursor.fetchone()[0]
        conn.close()
        
        if count == 0:
            import import_data
            import_data.import_data()
        else:
            print(f"Database already has {count} solutes, skipping import.")
    except Exception as e:
        print(f"Warning: Could not check/import data: {e}")
        try:
            import import_data
            import_data.import_data()
        except:
            pass

    # Load ML model
    print("Loading ML model...")
    try:
        from ml_model import get_predictor
        predictor = get_predictor()
        print("ML model loaded successfully!")
    except Exception as e:
        print(f"Warning: Could not load ML model: {e}")

    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask server on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == '__main__':
    main()
