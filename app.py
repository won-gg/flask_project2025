from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from database import DBhandler
import hashlib
import sys
application = Flask(__name__)
application.config["SECRET_KEY"] = "helloosp"
DB = DBhandler()

## 상품 임시 데이터 12개 (list.html & item_detail.html 사용)
item_data = {
    1: {'title': '100년 된 헤드셋', 'category': 'digitals', 'price': 10000, 'image_path': 'images/item-list/item-img1.jpg', 'fee': 0, 'trade': 'direct', 
        'description': '100주년 기념으로 기존에 사용하던 제품 싸게 판매합니다. 소리 잘 들리고 상태 좋습니다.', 'seller': 'ewhaosp1'},
    2: {'title': 'WONDER', 'category': 'books', 'price': 5000, 'image_path': 'images/item-list/item-img2.jpg', 'fee': 2500, 'trade': 'delivery', 
        'description': '읽으려고 샀는데 손이 안 가서 판매합니다. 거의 새 책입니다.', 'seller': 'ewhaosp2'},
    3: {'title': '검은색 버뮤다 팬츠', 'category': 'clothes', 'price': 10000, 'image_path': 'images/item-list/item-img3.jpg', 'fee': 0, 'trade': 'direct', 
        'description': '한두 번 입은 바지입니다. 상태 아주 좋습니다.', 'seller': 'ewhaosp3'},
    4: {'title': '고양이 마스킹 테이프', 'category': 'etc', 'price': 4000, 'image_path': 'images/item-list/item-img4.jpg', 'fee': 2500, 'trade': 'delivery', 
        'description': '처분하려고 팝니다. 마스킹 테이프 걸어둔 것까지 통째로 판매합니다. 반 정도 사용했습니다.', 'seller': 'ewhaosp4'},
    5: {'title': '국제법_김영석 저', 'category': 'books', 'price': 30000, 'image_path': 'images/item-list/item-img5.jpg', 'fee': 2500, 'trade': 'delivery', 
        'description': '작년 수업 시간에 사용한 교재입니다. 중요한 부분에 필기 있습니다. 오히려 도움이 될 수도 있습니다.', 'seller': 'ewhaosp5'},
    6: {'title': 'LG GRAM', 'category': 'digitals', 'price': 200000, 'image_path': 'images/item-list/item-img6.jpg', 'fee': 0, 'trade': 'direct', 
        'description': '새 노트북 구매로 기존 사용하던 노트북 판매합니다. 전원 이상 없고 화면에 키보드 자국 조금 남아있습니다. 카메라도 잘 작동됩니다.', 'seller': 'ewhaosp6'},
    7: {'title': '아이폰 5s', 'category': 'digitals', 'price': 30000, 'image_path': 'images/item-list/item-img7.jpg', 'fee': 2500, 'trade': 'delivery', 
        'description': '배터리 고장으로 전원이 안 들어옵니다. 바로 사용은 어렵고, A/S 후 사용 가능할 듯 싶습니다. 싸게 판매합니다.', 'seller': 'ewhaosp7'},
    8: {'title': '폴로 랄프 로렌 바람막이', 'category': 'clothes', 'price': 120000, 'image_path': 'images/item-list/item-img8.jpg', 'fee': 0, 'trade': 'direct',
        'description': '온라인 구매했는데 제 생각보다 얇아서 판매합니다. 택 붙어있는 거진 새 상품입니다.', 'seller': 'ewhaosp8'},
    9: {'title': '2p책예시', 'category': 'books', 'price': 30000, 'image_path': 'images/item-list/item-img5.jpg', 'fee': 2500, 'trade': 'delivery', 
        'description':'가나다라', 'seller': 'ewhaosp9'},
    10: {'title': '2p노트북예시', 'category': 'digitals', 'price': 200000, 'image_path': 'images/item-list/item-img6.jpg', 'fee': 0, 'trade': 'direct', 
        'description': '가나다', 'seller': 'ewhaosp10'},
    11: {'title': '2p핸드폰예시', 'category': 'digitals', 'price': 30000, 'image_path': 'images/item-list/item-img7.jpg', 'fee': 2500, 'trade': 'delivery', 
        'description': '가나', 'seller': 'ewhaosp11'},
    12: {'title': '2p의류예시', 'category': 'clothes', 'price': 120000, 'image_path': 'images/item-list/item-img8.jpg', 'fee': 0, 'trade': 'direct',
        'description': '가', 'seller': 'ewhaosp12'}
}

@application.route("/")
def hello():
  return render_template("index.html", user_id=session.get("id"), user_nickname=session.get("nickname"))

@application.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        id = request.form['id']
        pw = request.form['pw']
        pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
        nickname = DB.find_user(id, pw_hash)
        
        if nickname:
            session['id'] = id
            session['nickname'] = nickname
            return redirect(url_for('hello'))
        else:
            flash("잘못된 ID, PW")
            return redirect(url_for('login'))

    return render_template("login.html")

@application.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('hello'))

@application.route("/signup")
def signup():
  return render_template("signup.html")

@application.route("/signup_post", methods=['POST'])
def register_user():
  data=request.form
  pw=request.form['pw']
  pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
  if DB.insert_user(data,pw_hash):
    return render_template("login.html")
  else:
    flash("user id already exist!")
    return render_template("signup.html")
  
@application.route("/list")
def view_list():
  page = request.args.get("page",0,type=int)
  cat = (request.args.get("cat", "all") or "all").lower().strip()
  per_page=8
  per_row=4
  row_count=int(per_page/per_row)
  start_idx=per_page*page
  end_idx=per_page*(page+1)
  data = item_data
  #DB.get_items() #read the table
  all_data_items = list(item_data.items())
  if cat != "all":
    # 카테고리가 일치하는 아이템만 필터링
    filtered_items = [
    (iid, it) for iid, it in all_data_items 
      if str(it.get("category", "")).lower().strip() == cat
    ]
  else:
    # 'all'일 경우, 모든 아이템 사용
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
  return render_template(
     "list.html",
     datas=data.items(),
     row1=locals()['data_0'].items(),
     row2=locals()['data_1'].items(),
     limit=per_page,
     page = page,
     page_count=int((filtered_count/per_page)+1),
     cat=cat,
     total=filtered_count)

@application.route("/item_detail")
def view_item_detail():
  item_id = request.args.get('id', 1, type=int)
  item = item_data.get(item_id, item_data[1]) 

  return render_template(
    "item_detail.html",
    item_id=item_id,
    title=item['title'],
    category=item['category'].capitalize(),
    price=item['price'],
    image_path=item['image_path'],
    fee=item['fee'],
    trade=item['trade'],
    description=item['description'],
    seller=item['seller']
  )

@application.route("/reg_review_for/<item_id>/")
def reg_review_for(item_id):
    item_id_int = int(item_id)
    item = item_data.get(item_id_int)
    
    item_name = item.get('title')
    
    return render_template("reg_reviews.html", item_id=item_id_int, item_name=item_name)

@application.route("/review")
def view_review():
    reviews = {
        1: {"item_name": "100년 된 헤드셋", "title": "따뜻한 거래였어요", "rating": "A+", "author": "윤아", "author_rating": "A+", "content": "판매자분 너무 친절했어요!", "tags": ["친절", "포장깔끔"], "image_path": "images/item-list/item-img1.jpg"},
        2: {"item_name": "WONDEr", "title": "배송 빨랐어요", "rating": "A", "author": "민서", "author_rating": "A", "content": "상품 상태도 좋고 사진 그대로예요!", "tags": ["빠른배송", "상태좋음"], "image_path": "images/item-list/item-img2.jpg"},
        3: {"item_name": "검은색 버뮤다 팬츠", "title": "편하게 입기 좋아요", "rating": "A+", "author": "세은", "author_rating": "A+", "content": "너무 예쁜 소리예요 🎶", "tags": ["감성", "친절판매"], "image_path": "images/item-list/item-img3.jpg"},
        4: {"item_name": "고양이 마스킹 테이프", "title": "디자인이 귀여워서 자주 써요", "rating": "A", "author": "지수", "author_rating": "A", "content": "포장이 너무 예뻤어요 ☕️", "tags": ["예쁜포장", "선물추천"], "image_path": "images/item-list/item-img4.jpg"},
        5: {"item_name": "국제법-김영석 저", "title": "상태 좋아서 거래 만족스러워요 ", "rating": "A", "author": "윤아", "author_rating": "A+", "content": "작동도 잘 되고 예뻐요!", "tags": ["만족", "디자인좋음"], "image_path": "images/item-list/item-img5.jpg"},
        6: {"item_name": "엘지 그램", "title": "좋은 가격에 구매해서 만족스럽습니다.", "rating": "A+", "author": "윤아", "author_rating": "A+", "content": "직접 만드셨다니 대단해요!", "tags": ["친절", "퀄리티굿"], "image_path": "images/item-list/item-img6.jpg"},
        7: {"item_name": "아이폰 5s", "title": "찾던 매물인데 찾아서 기뻐요.", "rating": "A", "author": "세은", "author_rating": "A", "content": "잘 작동하고 고급스러워요!", "tags": ["정확한설명", "좋은거래"], "image_path": "images/item-list/item-img7.jpg"},
        8: {"item_name": "랄프로렌 바람막이", "title": "소장 가치 있어요", "rating": "A+", "author": "하늘", "author_rating": "A+", "content": "디자인이 너무 마음에 들어요!", "tags": ["빈티지", "소장추천"], "image_path": "images/item-list/item-img8.jpg"}
    }
    return render_template("review.html", reviews=reviews)

@application.route("/review/<int:id>")
def review_detail(id):
    data = {
        1: {"item_name": "100년 된 헤드셋", "title": "따뜻한 거래였어요", "rating": "A+", "author": "윤아", "author_rating": "A+", "content": "판매자분 너무 친절했어요!", "tags": ["친절", "포장깔끔"], "image_path": "images/item-list/item-img1.jpg"},
        2: {"item_name": "WONDEr", "title": "배송 빨랐어요", "rating": "A", "author": "민서", "author_rating": "A", "content": "상품 상태도 좋고 사진 그대로예요!", "tags": ["빠른배송", "상태좋음"], "image_path": "images/item-list/item-img2.jpg"},
        3: {"item_name": "검은색 버뮤다 팬츠", "title": "편하게 입기 좋아요", "rating": "A+", "author": "세은", "author_rating": "A+", "content": "너무 예쁜 소리예요 🎶", "tags": ["감성", "친절판매"], "image_path": "images/item-list/item-img3.jpg"},
        4: {"item_name": "고양이 마스킹 테이프", "title": "디자인이 귀여워서 자주 써요", "rating": "A", "author": "지수", "author_rating": "A", "content": "포장이 너무 예뻤어요 ☕️", "tags": ["예쁜포장", "선물추천"], "image_path": "images/item-list/item-img4.jpg"},
        5: {"item_name": "국제법-김영석 저", "title": "상태 좋아서 거래 만족스러워요 ", "rating": "A", "author": "윤아", "author_rating": "A+", "content": "작동도 잘 되고 예뻐요!", "tags": ["만족", "디자인좋음"], "image_path": "images/item-list/item-img5.jpg"},
        6: {"item_name": "엘지 그램", "title": "좋은 가격에 구매해서 만족스럽습니다.", "rating": "A+", "author": "윤아", "author_rating": "A+", "content": "직접 만드셨다니 대단해요!", "tags": ["친절", "퀄리티굿"], "image_path": "images/item-list/item-img6.jpg"},
        7: {"item_name": "아이폰 5s", "title": "찾던 매물인데 찾아서 기뻐요.", "rating": "A", "author": "세은", "author_rating": "A", "content": "잘 작동하고 고급스러워요!", "tags": ["정확한설명", "좋은거래"], "image_path": "images/item-list/item-img7.jpg"},
        8: {"item_name": "랄프로렌 바람막이", "title": "소장 가치 있어요", "rating": "A+", "author": "하늘", "author_rating": "A+", "content": "디자인이 너무 마음에 들어요!", "tags": ["빈티지", "소장추천"], "image_path": "images/item-list/item-img8.jpg"}
    }

    review = data.get(id)
    if not review:
        abort(404)

    return render_template("review_detail.html", review=review)


@application.route("/reg_items")
def reg_item():
  return render_template("reg_items.html")

@application.route("/reg_reviews")
def reg_review():
  return render_template("reg_reviews.html")

@application.route("/reg_review_post", methods=['POST'])
def reg_review_post():
    data=request.form
    image_file = request.files["file"]
    image_file.save("static/images/{}".format(image_file.filename))
    DB.reg_review(data, image_file.filename)
    return redirect(url_for('view_review'))

@application.route("/submit_item")
def reg_item_submit():
  name=request.args.get("name")
  seller=request.args.get("seller")
  addr=request.args.get("addr")
  email=request.args.get("email")
  category=request.args.get("category")
  card=request.args.get("card")
  status=request.args.get("status")
  phone=request.args.get("phone")

  print(name,seller,addr,email,category,card,status,phone)
  return render_template("reg_items.html")

@application.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post():
    # 파일 받기
    image_file = request.files["file"]
    image_path = f"static/images/{image_file.filename}"
    image_file.save(image_path)
    data = request.form

    DB.insert_item(data['name'], data, image_file.filename)

    return render_template("result.html", data= data, img_path = "static/images/{}".format(image_file.filename))

@application.route("/profile")
def profile():
  return render_template("profile.html")

@application.route('/show_heart/<name>/', methods=['GET'])
def show_heart(name):
    if 'id' not in session:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
        
    my_heart = DB.get_heart_byname(session['id'],name)
    if not my_heart:
        my_heart = {"interested": "N"}
        
    return jsonify({'my_heart': my_heart})

@application.route('/like/<name>/', methods=['POST'])
def like(name):
    if 'id' not in session:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
        
    my_heart = DB.update_heart(session['id'],'Y',name)
    return jsonify({'msg': '좋아요 완료!'})

@application.route('/unlike/<name>/', methods=['POST'])
def unlike(name):
    if 'id' not in session:
        return jsonify({'error': '로그인이 필요합니다.'}), 401
        
    my_heart = DB.update_heart(session['id'],'N',name)
    return jsonify({'msg': '안좋아요 완료!'})

if __name__ == "__main__":
  application.run(host='0.0.0.0', debug=True)