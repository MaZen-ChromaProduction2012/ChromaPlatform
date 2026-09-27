from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, User, Order, Review, ChatMessage

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

def require_admin():
    return current_user.is_authenticated and current_user.role == 'admin'

@admin_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    if not require_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    total_users = User.query.count()
    total_orders = Order.query.count()
    active_orders = Order.query.filter(Order.status.notin_(['completed', 'cancelled'])).count()
    total_reviews = Review.query.count()

    return jsonify({
        'total_users': total_users,
        'total_orders': total_orders,
        'active_orders': active_orders,
        'total_reviews': total_reviews
    })

@admin_bp.route('/users/<int:user_id>/warn', methods=['POST'])
@login_required
def warn_user(user_id):
    if not require_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    user = User.query.get_or_404(user_id)
    banned = user.add_warning()
    db.session.commit()

    return jsonify({
        'success': True,
        'user_id': user.id,
        'warnings': user.warnings_count,
        'is_banned': banned,
        'message': f'تم توجيه إنذار للمستخدم {user.username}. عدد الإنذارات: {user.warnings_count}'
    })

@admin_bp.route('/users/<int:user_id>/ban-toggle', methods=['POST'])
@login_required
def toggle_ban(user_id):
    if not require_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    user = User.query.get_or_404(user_id)
    user.is_banned = not user.is_banned
    db.session.commit()

    return jsonify({
        'success': True,
        'is_banned': user.is_banned,
        'message': 'تم حظر المستخدم' if user.is_banned else 'تم إلغاء حظر المستخدم'
    })

@admin_bp.route('/reviews/<int:review_id>/toggle-hide', methods=['POST'])
@login_required
def toggle_review_hide(review_id):
    if not require_admin():
        return jsonify({'error': 'Unauthorized'}), 403

    review = Review.query.get_or_404(review_id)
    review.is_hidden = not review.is_hidden
    db.session.commit()

    return jsonify({'success': True, 'is_hidden': review.is_hidden})
