from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from database import DBhandler # DB 사용을 위해 임포트
import hashlib

bp = Blueprint('auth', __name__)

# DB 인스턴스 생성 (또는 app.py에서 넘겨받은 것 사용)
DB = DBhandler()

@bp.route("/login", methods=['GET', 'POST'])
def login():
    next_page = request.args.get('next') or request.form.get('next')
    if not next_page or next_page == "None":
        next_page = url_for('item.view_list')

    if '/signup' in next_page or '/signup_post' in next_page:
        next_page = url_for('item.view_list')

    if request.method == 'POST':
        id = request.form['id']
        pw = request.form['pw']
        pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

        user_info = DB.find_user(id, pw_hash)
        
        if user_info:
            session['id'] = user_info['id']
            session['nickname'] = user_info['id']
            session['phoneNum'] = user_info['phoneNum']
            return redirect(next_page)
        else:
            flash("잘못된 ID, PW")
            return redirect(url_for('auth.login', next=next_page))

    return render_template("login.html", next_page=next_page)

@bp.route("/logout")
def logout():
    next_page = request.args.get('next')
    session.clear()
    return redirect(next_page or url_for('hello'))

@bp.route("/signup")
def signup():
  return render_template("signup.html")

@bp.route("/signup_post", methods=['POST'])
def register_user():
    data = request.form
    pw = data['pw']
    pw_check = data['pwCheck']

    if pw != pw_check:
        flash("비밀번호가 일치하지 않습니다.")
        return redirect(url_for('auth.signup'))
    
    if not DB.user_duplicate_check(data['id']):
        flash("이미 존재하는 아이디입니다.")
        return redirect(url_for('auth.signup'))
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

    DB.insert_user(data, pw_hash)
    return render_template("login.html")

@bp.route("/check_id/<userid>")
def check_id(userid):
    available = DB.user_duplicate_check(userid)
    return jsonify({"available": available})

@bp.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template("forgot_password.html")
    
    user_id = request.form['id']
    email = request.form['email']

    users = DB.db.child("user").get().val()

    if users is None:
        flash("가입 정보가 없습니다.")
        return redirect(url_for('auth.forgot_password'))

    for u in users.values():
        if u['id'] == user_id and u['email'] == email:
            return redirect(url_for('auth.reset_password', userid=user_id))
    flash("입력한 정보가 일치하지 않습니다.")
    return redirect(url_for('auth.forgot_password'))

@bp.route("/reset_password/<userid>", methods=['GET', 'POST'])
def reset_password(userid):
    if request.method == 'GET':
        return render_template("reset_password.html", userid=userid)

    pw = request.form['pw']
    pwCheck = request.form['pwCheck']

    if pw != pwCheck:
        flash("비밀번호가 일치하지 않습니다.")
        return redirect(url_for('auth.reset_password', userid=userid))

    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

    users = DB.db.child("user").get()
    for key, value in users.val().items():
        if value['id'] == userid:
            DB.db.child("user").child(key).update({"pw": pw_hash})

    flash("비밀번호가 성공적으로 변경되었습니다.")
    return redirect(url_for('auth.login'))
