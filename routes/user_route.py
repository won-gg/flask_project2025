from flask import Blueprint, abort, render_template, request, flash, redirect, url_for, session, jsonify
from database import DBhandler

bp = Blueprint('user', __name__)
DB = DBhandler()

## 프로필 페이지
@bp.route("/profile/<user_id>")
def profile(user_id):
    if session and session['id'] == user_id:
        liked_items = DB.get_liked_items_by_user(user_id)
    else:
        liked_items = {}
        user_manners_grade = None

    user_manners_grade = DB.get_manners_grade_by_userid(user_id)
    user_items = DB.get_items_by_user_id(user_id)
    user_reviews = DB.get_reviews_by_user(user_id)

    user_items_count = len(user_items) if user_items else 0
    user_reviews_count = len(user_reviews) if user_reviews else 0
    
    return render_template(
        "profile.html",
        user_id=user_id,
        liked_items=liked_items,
        user_items=user_items,
        user_reviews=user_reviews,
        user_items_count=user_items_count,
        user_reviews_count=user_reviews_count,
        user_manners_grade=user_manners_grade
    )


## 좋아요 상태 조회
@bp.route('/show_heart/<item_id>/', methods=['GET'])
def show_heart(item_id):
    if 'id' not in session:
        return jsonify({'error': '로그인이 필요합니다.'}), 401

    my_heart = DB.get_heart_byname(session['id'],item_id)
    if not my_heart:
        my_heart = {"interested": "N"}

    return jsonify({'my_heart': my_heart})

## 좋아요 / 좋아요취소 처리
@bp.route('/like/<item_id>/', methods=['POST'])
def like(item_id):
    if 'id' not in session:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
    
    item = DB.get_item_by_id(item_id)

    DB.update_heart (
        session['id'],
        'Y',
        item_id, 
        item['title'],
        item['img_path']
    )
    return jsonify({'msg': '좋아요 완료!'})

@bp.route('/unlike/<item_id>/', methods=['POST'])
def unlike(item_id):
    if 'id' not in session:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
    
    item = DB.get_item_by_id(item_id)

    DB.update_heart (
        session['id'],
        'N',
        item_id, 
        item['title'],
        item['img_path']
    )

    return jsonify({'msg': '좋아요 취소 완료!'}) # "안 좋아요" -> "좋아요 취소" 문구 변경
