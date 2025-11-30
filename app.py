from flask import Flask, abort, render_template, request, flash, redirect, url_for, session, jsonify
from database import DBhandler
import hashlib
import sys
application = Flask(__name__)
application.config["SECRET_KEY"] = "helloosp"
DB = DBhandler()


@application.route("/")
def hello():
  render_template("index.html", user_id=session.get("id"), user_nickname=session.get("nickname"))
  return view_list()

@application.route("/login", methods=['GET', 'POST'])
def login():
    next_page = request.args.get('next') or request.form.get('next')
    if not next_page or next_page == "None":
        next_page = url_for('view_list')

    if '/signup' in next_page or '/signup_post' in next_page:
        next_page = url_for('view_list')

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
            return redirect(url_for('login', next=next_page))

    return render_template("login.html", next_page=next_page)

@application.route("/logout")
def logout():
    next_page = request.args.get('next')
    session.clear()
    return redirect(next_page or url_for('hello'))

@application.route("/signup")
def signup():
  return render_template("signup.html")

@application.route("/signup_post", methods=['POST'])
def register_user():
    data = request.form
    pw = data['pw']
    pw_check = data['pwCheck']

    if pw != pw_check:
        flash("비밀번호가 일치하지 않습니다.")
        return redirect(url_for('signup'))
    
    if not DB.user_duplicate_check(data['id']):
        flash("이미 존재하는 아이디입니다.")
        return redirect(url_for('signup'))

    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

    DB.insert_user(data, pw_hash)
    return render_template("login.html")

@application.route("/check_id/<userid>")
def check_id(userid):
    available = DB.user_duplicate_check(userid)
    return jsonify({"available": available})

@application.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template("forgot_password.html")
    
    user_id = request.form['id']
    email = request.form['email']

    users = DB.db.child("user").get().val()

    if users is None:
        flash("가입 정보가 없습니다.")
        return redirect(url_for('forgot_password'))

    for u in users.values():
        if u['id'] == user_id and u['email'] == email:
            return redirect(url_for('reset_password', userid=user_id))

    flash("입력한 정보가 일치하지 않습니다.")
    return redirect(url_for('forgot_password'))

@application.route("/reset_password/<userid>", methods=['GET', 'POST'])
def reset_password(userid):
    if request.method == 'GET':
        return render_template("reset_password.html", userid=userid)

    pw = request.form['pw']
    pwCheck = request.form['pwCheck']

    if pw != pwCheck:
        flash("비밀번호가 일치하지 않습니다.")
        return redirect(url_for('reset_password', userid=userid))

    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

    users = DB.db.child("user").get()
    for key, value in users.val().items():
        if value['id'] == userid:
            DB.db.child("user").child(key).update({"pw": pw_hash})

    flash("비밀번호가 성공적으로 변경되었습니다.")
    return redirect(url_for('login'))

@application.route("/reg_items")
def reg_item():
  if 'id' not in session:
        flash("상품을 등록하려면 로그인이 필요합니다.")
        return redirect(url_for('login'))
  
  user_id = session.get('id')
  user_phone = session.get('phoneNum')

  seller_manners_grade = DB.get_user_manners_grade(user_id)

  return render_template("reg_items.html", user_id=user_id, user_phone = user_phone, seller_manners_grade=seller_manners_grade)

@application.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
    if 'id' not in session:
        flash("상품을 등록하려면 로그인이 필요합니다.")
        return redirect(url_for('login'))
    
    image_files = request.files.getlist("file") #파일 여러 장 받기
    image_paths = [] 

    for file in image_files:
        if file.filename != '':
            file.save("static/images/{}".format(file.filename))
            image_paths.append(file.filename)

    data = request.form

    seller_id = session.get('id')
    seller_manners_grade = DB.get_user_manners_grade(seller_id)

    
    DB.insert_item(data, image_paths, seller_manners_grade)

    return redirect(url_for('view_list'))

## 상품 리스트 페이지 + 검색 기능 추가
@application.route("/list")
def view_list():
    page = request.args.get("page",0,type=int)
    cat = (request.args.get("cat", "all") or "all").lower().strip()
    q = (request.args.get("q", "") or "").lower().strip()
    per_page=8
    per_row=4
    row_count=int(per_page/per_row)
    start_idx=per_page*page
    end_idx=per_page*(page+1)

    data = DB.get_items()

    if data is None:
        data = {}
    elif isinstance(data, list):
            new_data = {}
            for i, item in enumerate(data):
                if item is not None:
                    new_data[str(i)] = item
            data = new_data
    
    all_data_items = list(data.items())

    # 필터링: 카테고리 및 검색어
    if cat != "all" or q != "":
        filtered_items = []
        for iid, it in all_data_items:
            item_cat = str(it.get("category", "")).lower().strip()
            item_name = str(it.get("title", "")).lower()
            item_desc = str(it.get("explain", "")).lower()

            if (cat == "all" or item_cat == cat):   # 카테고리 조건
                if (q == "" or q in item_name or q in item_desc):  # 검색 조건
                    filtered_items.append((iid, it))
    else:
        filtered_items = all_data_items

    filtered_count = len(filtered_items)
    current_page_items = filtered_items[start_idx:end_idx]

    data = dict(current_page_items)
    tot_count = len(data)
    for i in range(row_count):
        if (i==row_count -1) and (tot_count%per_row != 0):
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:])
        else:
            locals()['data_{}'.format(i)] = dict(list(data.items())[i*per_row:(i+1)*per_row])

    data = {}
    for iid, it in current_page_items:
        heart_cnt = DB.count_hearts_for_item(iid)
        it['heart_count'] = heart_cnt
        data[iid] = it


    return render_template(
        "list.html",
        datas=data.items(),
        row1=locals()['data_0'].items(),
        row2=locals()['data_1'].items(),
        limit=per_page,
        page = page,
        page_count=int((filtered_count/per_page)+1),
        cat=cat,
        total=filtered_count,
        q=q,
    )


@application.route("/item_detail")
def view_item_detail():
  item_id = request.args.get('id', type=int)

  item = DB.get_item_by_id(item_id) 

  heart_cnt = DB.count_hearts_for_item(str(item_id))

  seller_grade = item.get("seller_manners_grade", "A+")
  return render_template(
    "item_detail.html",
    item_id=item_id,
    title=item['title'],
    category=item['category'].capitalize(),
    price=item['price'],
    image_path=item['img_path'],
    fee=2500, #택배 기본값
    trade=item['trade'],
    description=item['explain'],
    seller=item['seller'],
    heart_cnt=heart_cnt,
    sale=item.get('sale', 'Y'),
    seller_manners_grade=seller_grade,
  )


@application.route("/reg_reviews")
def reg_review():
  return render_template("reg_reviews.html")

@application.route("/reg_review_for/<item_id>/")
def reg_review_for(item_id):
    if 'id' not in session:
        flash("리뷰를 작성하려면 로그인이 필요합니다.")
        return redirect(url_for('login'))

    item = DB.get_item_by_id(item_id)
    
    item_name = item['title']
    reviewer_id = session.get('id')
    reviewer_manners_grade = DB.get_user_manners_grade(reviewer_id)
    
    return render_template("reg_reviews.html", item_id=item_id, item_name=item_name,
                            reviewer_id=reviewer_id,reviewer_manners_grade=reviewer_manners_grade)

@application.route("/reg_review_post", methods=['POST'])
def reg_review_post():

    image_files = request.files.getlist("file") #파일 여러 장 받기
    image_paths = [] 

    for file in image_files:
        if file.filename != '':
            file.save("static/images/{}".format(file.filename))
            image_paths.append(file.filename)


    data=request.form

    reviewer_id = session.get('id')
    reviewer_manners_grade = DB.get_user_manners_grade(reviewer_id)

    DB.reg_review(data, image_paths, reviewer_manners_grade)

    return redirect(url_for('view_review'))

@application.route("/review")
def view_review():
    page = request.args.get("page", 0, type=int)
    per_page = 8
    start_idx = per_page * page
    end_idx = per_page * (page + 1)

    reviews_data = DB.get_reviews()

    if not reviews_data:
        reviews_data = {}

    # Firebase에서 단일 리뷰가 dict가 아닌 list로 반환되는 경우 처리
    elif isinstance(reviews_data, list):
        clean_reviews = {}
        for i, item in enumerate(reviews_data):
            if item is not None:
                clean_reviews[str(i)] = item
        reviews_data = clean_reviews

    # 전체 리뷰 개수
    total_count = len(reviews_data)
    
    # 페이지네이션을 위한 리뷰 리스트 생성
    all_reviews_items = list(reviews_data.items())
    
    # 현재 페이지에 표시할 리뷰만 선택
    current_page_reviews = all_reviews_items[start_idx:end_idx]
    current_reviews = dict(current_page_reviews)
    
    # 전체 페이지 수 계산
    page_count = int((total_count / per_page) + 1) if total_count > 0 else 1

    return render_template(
        "review.html", 
        reviews=current_reviews, 
        total=total_count,
        page=page,
        page_count=page_count
    )


@application.route("/review_detail/<item_id>")
def view_review_detail(item_id):

    review_data = DB.get_review_by_id(item_id)

    if not review_data:
        abort(404)

    img_path = review_data.get("img_path", "")

    review = {
        "item_name": review_data.get("item_name", ""),
        "rating": review_data.get("rating", ""),
        "title": review_data.get("title", ""),
        "content": review_data.get("content", ""),
        "tags": [],  # 데이터베이스에 tags 필드가 없으므로 빈 리스트
        "author": review_data.get("reviewer_id", "익명"),  # reviewer_id를 author로 사용
        "author_avg_rating": review_data.get("reviewer_manners_grade", "B+"),
        "img_path": img_path
    }

    return render_template("review_detail.html", review = review)


## 프로필 페이지
@application.route("/profile/<user_id>")
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
@application.route('/show_heart/<item_id>/', methods=['GET'])
def show_heart(item_id):
    if 'id' not in session:
        return jsonify({'error': '로그인이 필요합니다.'}), 401

    my_heart = DB.get_heart_byname(session['id'],item_id)
    if not my_heart:
        my_heart = {"interested": "N"}

    return jsonify({'my_heart': my_heart})

## 좋아요 / 좋아요취소 처리
@application.route('/like/<item_id>/', methods=['POST'])
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

@application.route('/unlike/<item_id>/', methods=['POST'])
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

# 판매 완료 기능
@application.route("/purchase/<item_id>/", methods=['POST'])
def purchase_item(item_id):
    if 'id' not in session:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
    item = DB.get_item_by_id(item_id)
    if item.get("sale") == "N":
        return jsonify({'error': '이미 판매 완료된 상품입니다.'}), 400
    DB.update_item_sale(item_id, "N")

    return jsonify({'msg': '구매 완료!'})


if __name__ == "__main__":
  application.run(host='0.0.0.0', debug=True)