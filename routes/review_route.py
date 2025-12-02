from flask import Blueprint, abort, render_template, request, flash, redirect, url_for, session
from database import DBhandler

bp = Blueprint('review', __name__)
DB = DBhandler()

@bp.route("/reg_reviews")
def reg_review():
  return render_template("reg_reviews.html")

@bp.route("/reg_review_for/<item_id>/")
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

@bp.route("/reg_review_post", methods=['POST'])
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

    return redirect(url_for('review.view_review'))

@bp.route("/review")
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
    
    # img_path가 문자열인 경우 리스트로 변환 (일관성 유지)
    for review_id, review in current_reviews.items():
        if isinstance(review, dict) and 'img_path' in review:
            if not isinstance(review['img_path'], list):
                # 문자열인 경우 리스트로 변환
                review['img_path'] = [review['img_path']] if review['img_path'] else []
    
    # 전체 페이지 수 계산
    page_count = int((total_count / per_page) + 1) if total_count > 0 else 1

    return render_template(
        "review.html", 
        reviews=current_reviews, 
        total=total_count,
        page=page,
        page_count=page_count
    )


@bp.route("/review_detail/<item_id>")
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
