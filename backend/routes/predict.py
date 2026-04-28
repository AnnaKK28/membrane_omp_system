"""
Prediction routes.
POST /api/predict
GET /api/experiments
GET /api/statistics
"""
from flask import Blueprint, request, jsonify
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection
from ml_model import get_predictor

predict_bp = Blueprint('predict', __name__, url_prefix='/api')


@predict_bp.route('/predict', methods=['POST'])
def predict():
    """
    Predict rejection rate for a solute-membrane pair.
    Input: { solute_id: int, membrane_id: int }
    Output: { rejection_rate: float }
    """
    data = request.get_json()

    if not data:
        return jsonify({'success': False, 'error': 'No input data provided'}), 400

    solute_id = data.get('solute_id')
    membrane_id = data.get('membrane_id')

    if not solute_id or not membrane_id:
        return jsonify({'success': False, 'error': 'solute_id and membrane_id are required'}), 400

    # Fetch solute features
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name, MW, charge, logD FROM solute WHERE id = ?", (solute_id,))
    solute = cursor.fetchone()

    cursor.execute("SELECT name, MWCO, contact_angle, zeta_potential FROM membrane WHERE id = ?", (membrane_id,))
    membrane = cursor.fetchone()

    conn.close()

    if solute is None:
        return jsonify({'success': False, 'error': f'Solute with id={solute_id} not found'}), 404

    if membrane is None:
        return jsonify({'success': False, 'error': f'Membrane with id={membrane_id} not found'}), 404

    # Build feature dict for model
    feature_dict = {
        'MW': solute['MW'],
        'charge': solute['charge'],
        'logD': solute['logD'],
        'MWCO': membrane['MWCO'],
        'contact_angle': membrane['contact_angle'],
        'zeta_potential': membrane['zeta_potential']
    }

    # Predict
    predictor = get_predictor()
    rejection_rate = predictor.predict_from_dict(feature_dict)

    # Round to 2 decimal places
    rejection_rate = round(rejection_rate, 2)

    return jsonify({
        'success': True,
        'data': {
            'solute_id': solute_id,
            'solute_name': solute['name'],
            'membrane_id': membrane_id,
            'membrane_name': membrane['name'],
            'rejection_rate': rejection_rate,
            'features': feature_dict
        }
    })


@predict_bp.route('/experiments', methods=['GET'])
def list_experiments():
    """List experiments with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)

    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM experiment")
    total = cursor.fetchone()['total']

    cursor.execute("""
        SELECT e.id, e.rejection_rate,
               s.name as solute_name, s.MW, s.charge, s.logD,
               m.name as membrane_name, m.membrane_type, m.MWCO, m.contact_angle, m.zeta_potential
        FROM experiment e
        JOIN solute s ON e.solute_id = s.id
        JOIN membrane m ON e.membrane_id = m.id
        ORDER BY e.id DESC
        LIMIT ? OFFSET ?
    """, (per_page, offset))

    rows = cursor.fetchall()
    conn.close()

    results = [dict(row) for row in rows]
    return jsonify({
        'success': True,
        'data': results,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    })


@predict_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get basic statistics about the dataset."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM solute")
    solute_count = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM membrane")
    membrane_count = cursor.fetchone()['count']

    cursor.execute("SELECT COUNT(*) as count FROM experiment")
    experiment_count = cursor.fetchone()['count']

    cursor.execute("SELECT AVG(rejection_rate) as avg_rejection, MIN(rejection_rate) as min_rejection, MAX(rejection_rate) as max_rejection FROM experiment")
    stats = cursor.fetchone()

    cursor.execute("""
        SELECT s.name as solute_name, COUNT(*) as experiment_count
        FROM experiment e
        JOIN solute s ON e.solute_id = s.id
        GROUP BY s.name
        ORDER BY experiment_count DESC
        LIMIT 10
    """)
    top_solutes = [dict(row) for row in cursor.fetchall()]

    cursor.execute("""
        SELECT m.name as membrane_name, COUNT(*) as experiment_count
        FROM experiment e
        JOIN membrane m ON e.membrane_id = m.id
        GROUP BY m.name
        ORDER BY experiment_count DESC
        LIMIT 10
    """)
    top_membranes = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return jsonify({
        'success': True,
        'data': {
            'solute_count': solute_count,
            'membrane_count': membrane_count,
            'experiment_count': experiment_count,
            'rejection_stats': {
                'avg': round(stats['avg_rejection'], 2) if stats['avg_rejection'] else None,
                'min': round(stats['min_rejection'], 2) if stats['min_rejection'] else None,
                'max': round(stats['max_rejection'], 2) if stats['max_rejection'] else None,
            },
            'top_solutes': top_solutes,
            'top_membranes': top_membranes
        }
    })


# Additional chart data endpoint
@predict_bp.route('/chart/membrane_comparison', methods=['GET'])
def chart_membrane_comparison():
    """Get rejection rates for all membranes for a given solute."""
    solute_id = request.args.get('solute_id', type=int)
    if not solute_id:
        return jsonify({'success': False, 'error': 'solute_id is required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name, MW, charge, logD FROM solute WHERE id = ?", (solute_id,))
    solute = cursor.fetchone()

    if not solute:
        conn.close()
        return jsonify({'success': False, 'error': 'Solute not found'}), 404

    cursor.execute("""
        SELECT m.name, e.rejection_rate
        FROM experiment e
        JOIN membrane m ON e.membrane_id = m.id
        WHERE e.solute_id = ?
        ORDER BY e.rejection_rate DESC
    """, (solute_id,))

    rows = cursor.fetchall()
    conn.close()

    return jsonify({
        'success': True,
        'data': {
            'solute': dict(solute),
            'membranes': [dict(row) for row in rows]
        }
    })


@predict_bp.route('/chart/solute_comparison', methods=['GET'])
def chart_solute_comparison():
    """Get rejection rates for all solutes for a given membrane."""
    membrane_id = request.args.get('membrane_id', type=int)
    if not membrane_id:
        return jsonify({'success': False, 'error': 'membrane_id is required'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name, MWCO, contact_angle, zeta_potential FROM membrane WHERE id = ?", (membrane_id,))
    membrane = cursor.fetchone()

    if not membrane:
        conn.close()
        return jsonify({'success': False, 'error': 'Membrane not found'}), 404

    cursor.execute("""
        SELECT s.name, e.rejection_rate
        FROM experiment e
        JOIN solute s ON e.solute_id = s.id
        WHERE e.membrane_id = ?
        ORDER BY e.rejection_rate DESC
    """, (membrane_id,))

    rows = cursor.fetchall()
    conn.close()

    return jsonify({
        'success': True,
        'data': {
            'membrane': dict(membrane),
            'solutes': [dict(row) for row in rows]
        }
    })
