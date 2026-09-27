import sys
from app import create_app
from models import db, User

def add_admin(username, email, password):
    app = create_app()
    with app.app_context():
        existing = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing:
            print(f"[-] المستخدم {username} موجود بالفعل.")
            return
        
        admin = User(username=username, email=email, role='admin', phone='01000000000')
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"[+] تم إنشاء حساب الأدمن بنجاح: {username}")

if __name__ == '__main__':
    u = sys.argv[1] if len(sys.argv) > 1 else 'admin'
    e = sys.argv[2] if len(sys.argv) > 2 else 'admin@chromaproduction.com'
    p = sys.argv[3] if len(sys.argv) > 3 else 'admin123456'
    add_admin(u, e, p)
