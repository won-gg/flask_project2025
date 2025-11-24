document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("reviewModal");
    const closeBtn = document.querySelector(".close");
    const modalImg = document.getElementById("modal-image");
    const modalItem = document.getElementById("modal-item");
    const modalRating = document.getElementById("modal-rating");
    const modalTitle = document.getElementById("modal-title");
    const modalContent = document.getElementById("modal-content");
    const modalTags = document.getElementById("modal-tags");
    const modalAuthor = document.getElementById("modal-author");
    const modalAuthorRating = document.getElementById("modal-author-rating");
  
    // 모든 리뷰 카드 선택
    const cards = document.querySelectorAll(".review-card");
  
    // 리뷰 데이터 (Flask 템플릿에서 JSON으로 주입)
    const reviewData = JSON.parse(document.getElementById("reviewData").textContent);
  
    // 카드 클릭 시 모달 열기
    cards.forEach(card => {
      card.addEventListener("click", () => {
        const id = card.dataset.id;
        const data = reviewData[id];
        if (!data) return;
    
        // 이미지 4장 표시
        const modalImages = document.getElementById("modal-images");
        modalImages.innerHTML = Array(4).fill(0).map(() =>
          `<img src="/static/images/${data.img_path}" alt="리뷰 이미지">`
        ).join("");
    
        document.getElementById("modal-item").textContent = data.item_name;
        document.getElementById("modal-rating").textContent = `매너 학점: ${data.rating}`;
        document.getElementById("modal-title").textContent = data.title;
        document.getElementById("modal-content").textContent = data.content;
        document.getElementById("modal-author").textContent = data.reviewer_id;
        document.getElementById("modal-author-rating").textContent = `작성자 매너 점수: ${data.author_rating}`;
    
        const modalTags = document.getElementById("modal-tags");
        modalTags.innerHTML = "";
        if (data.tags && data.tags.length > 0) {
          data.tags.forEach(tag => {
            const span = document.createElement("span");
            span.textContent = `#${tag}`;
            modalTags.appendChild(span);
          });
        }
    
        modal.style.display = "flex";
        document.body.style.overflow = "hidden";
      });
    });
    
    
  
    // 닫기 버튼
    closeBtn.addEventListener("click", () => {
      modal.style.display = "none";
      document.body.style.overflow = "auto";
    });
  
    // 모달 바깥 클릭 시 닫기
    window.addEventListener("click", (e) => {
      if (e.target === modal) {
        modal.style.display = "none";
        document.body.style.overflow = "auto";
      }
    });
  });
  