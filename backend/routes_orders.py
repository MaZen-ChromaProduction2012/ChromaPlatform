import os
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, current_app, send_from_directory
from flask_login import login_required, current_user
from models import db, Order, User, ChatMessage, Review
import subprocess

orders_bp = Blueprint('orders', __name__, url_prefix='/api/orders')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

STATUS_MAP = {
    'received': ('تم استلام الطلب وبانتظار بدء العمل', 10),
    'downloading': ('جاري تحميل وفرز الماتريال الخام', 25),
    'rough_cut': ('جاري التقطيع الأولي والمزامنة', 45),
    'audio_sync': ('جاري ضبط هندسة الصوت والمؤثرات الصوتية', 65),
    'color_grade': ('جاري تصحيح وتدريج الألوان (Color Grading)', 80),
    'vfx': ('إضافة الموشن جرافيك والمؤثرات البصرية', 90),
    'in_review': ('جاهز للمعاينة والمراجعة النهائية', 95),
    'completed': ('تم التسليم النهائي بنجاح', 100),
    'cancelled': ('تم إلغاء الطلب', 0)
}

@orders_bp.route('', methods=['GET'])
@login_required
def list_orders():
    if current_user.role == 'admin':
        orders = Order.query.order_by(Order.created_at.desc()).all()
    elif current_user.role == 'editor':
        orders = Order.query.filter((Order.editor_id == current_user.id) | (Order.editor_id == None)).order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.filter_by(client_id=current_user.id).order_by(Order.created_at.desc()).all()

    return jsonify({
        'orders': [{
            'id': o.id,
            'title': o.title,
            'service_type': o.service_type,
            'status': o.status,
            'status_text': o.status_text_ar,
            'progress': o.progress_percentage,
            'client_name': o.client.username,
            'editor_name': o.editor.username if o.editor else 'غير مسند لمونتير',
            'file_name': o.uploaded_file_name,
            'delivered_url': o.delivered_file_url,
            'created_at': o.created_at.strftime('%Y-%m-%d %H:%M')
        } for o in orders]
    })

@orders_bp.route('/create', methods=['POST'])
@login_required
def create_order():
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    service_type = request.form.get('service_type', 'video_editing')

    if not title or not description:
        return jsonify({'success': False, 'message': 'عنوان ووصف الطلب مطلوبين'}), 400

    filename = None
    filesize = None
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            sec_name = secure_filename(file.filename)
            unique_filename = f"{current_user.id}_{int(os.times()[4])}_{sec_name}"
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(save_path)
            filename = unique_filename
            filesize = f"{round(os.path.getsize(save_path) / (1024 * 1024), 2)} MB"

    order = Order(
        title=title,
        description=description,
        service_type=service_type,
        client_id=current_user.id,
        uploaded_file_name=filename,
        uploaded_file_size=filesize,
        status='received',
        status_text_ar=STATUS_MAP['received'][0],
        progress_percentage=STATUS_MAP['received'][1]
    )
    db.session.add(order)
    db.session.commit()

    return jsonify({'success': True, 'message': 'تم إنشاء الطلب بنجاح', 'order_id': order.id})

@orders_bp.route('/<int:order_id>/update-status', methods=['POST'])
def update_status(order_id):
    # Can be called by editor via web OR internal API by Telegram Bot
    api_key = request.headers.get('X-Internal-Key')
    is_internal_bot = (api_key == current_app.config['INTERNAL_API_KEY'])

    if not is_internal_bot and not (current_user.is_authenticated and current_user.role in ['editor', 'admin']):
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json() or {}
    new_status = data.get('status')
    custom_text = data.get('custom_text')
    progress = data.get('progress')

    order = Order.query.get_or_404(order_id)
    if new_status in STATUS_MAP:
        order.status = new_status
        order.status_text_ar = custom_text or STATUS_MAP[new_status][0]
        order.progress_percentage = progress if progress is not None else STATUS_MAP[new_status][1]
    elif custom_text:
        order.status_text_ar = custom_text
        if progress is not None:
            order.progress_percentage = progress

    db.session.commit()
    return jsonify({
        'success': True,
        'order_id': order.id,
        'status': order.status,
        'status_text': order.status_text_ar,
        'progress': order.progress_percentage
    })

@orders_bp.route('/<int:order_id>/download-zip', methods=['GET'])
@login_required
def download_zip(order_id):
    if current_user.role not in ['editor', 'admin']:
        return jsonify({'error': 'Unauthorized'}), 403

    order = Order.query.get_or_404(order_id)
    if not order.uploaded_file_name:
        return jsonify({'error': 'لا توجد ملفات مرفوعة'}), 404

    return send_from_directory(current_app.config['UPLOAD_FOLDER'], order.uploaded_file_name, as_attachment=True)
