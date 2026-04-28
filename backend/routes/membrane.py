"""
Membrane routes.
GET /api/membrane/search?name=
GET /api/membrane/list
GET /api/membrane/<id>
"""
from flask import Blueprint, request, jsonify
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection

membrane_bp = Blueprint('membrane', __name__, url_prefix='/api/membrane')


@membrane_bp.route('/search', methods=['GET'])
def search_membrane():
    """Search membranes by name (fuzzy search)."""
    name = request.args.get('name', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    if name:
        cursor.execute(
            """SELECT id, name, membrane_type, MWCO, contact_angle, zeta_potential
               FROM membrane WHERE name LIKE ? ORDER BY name LIMIT 20""",
            (f'%{name}%',)
        )
    else:
        cursor.execute(
            "SELECT id, name, membrane_type, MWCO, contact_angle, zeta_potential FROM membrane ORDER BY name LIMIT 20"
        )

    rows = cursor.fetchall()
    conn.close()

    results = [dict(row) for row in rows]
    return jsonify({
        'success': True,
        'data': results,
        'count': len(results)
    })


@membrane_bp.route('/list', methods=['GET'])
def list_membranes():
    """List all membranes with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)

    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM membrane")
    total = cursor.fetchone()['total']

    cursor.execute(
        "SELECT id, name, membrane_type, MWCO, contact_angle, zeta_potential FROM membrane ORDER BY name LIMIT ? OFFSET ?",
        (per_page, offset)
    )
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


@membrane_bp.route('/<int:membrane_id>', methods=['GET'])
def get_membrane(membrane_id):
    """Get a single membrane by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, membrane_type, MWCO, contact_angle, zeta_potential FROM membrane WHERE id = ?",
        (membrane_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return jsonify({'success': False, 'error': 'Membrane not found'}), 404

    return jsonify({'success': True, 'data': dict(row)})
