"""
Solute (pollutant) routes.
GET /api/solute/search?name=
GET /api/solute/list
GET /api/solute/<id>
"""
from flask import Blueprint, request, jsonify
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection

solute_bp = Blueprint('solute', __name__, url_prefix='/api/solute')


@solute_bp.route('/search', methods=['GET'])
def search_solute():
    """Search solutes by name (fuzzy search)."""
    name = request.args.get('name', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor()

    if name:
        cursor.execute(
            """SELECT id, name, MW, charge, logD FROM solute
               WHERE name LIKE ? ORDER BY name LIMIT 20""",
            (f'%{name}%',)
        )
    else:
        cursor.execute("SELECT id, name, MW, charge, logD FROM solute ORDER BY name LIMIT 20")

    rows = cursor.fetchall()
    conn.close()

    results = [dict(row) for row in rows]
    return jsonify({
        'success': True,
        'data': results,
        'count': len(results)
    })


@solute_bp.route('/list', methods=['GET'])
def list_solutes():
    """List all solutes with pagination."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)  # Cap at 100

    offset = (page - 1) * per_page

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM solute")
    total = cursor.fetchone()['total']

    cursor.execute(
        "SELECT id, name, MW, charge, logD FROM solute ORDER BY name LIMIT ? OFFSET ?",
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


@solute_bp.route('/<int:solute_id>', methods=['GET'])
def get_solute(solute_id):
    """Get a single solute by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, MW, charge, logD FROM solute WHERE id = ?", (solute_id,))
    row = cursor.fetchone()
    conn.close()

    if row is None:
        return jsonify({'success': False, 'error': 'Solute not found'}), 404

    return jsonify({'success': True, 'data': dict(row)})
