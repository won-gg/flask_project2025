 // 1) === 가격 계산(직거래면 배송비(fee) 0) ===

  (() => {
  const $root = document.querySelector('.detail-page');
  if (!$root) return;

  // 기본 데이터 추출
  const price = +$root.dataset.price || 0;
  const fee = +$root.dataset.fee || 0;
  const trade = ($root.dataset.trade || 'delivery').toLowerCase();

  // 계산
  const feeApplied = trade === 'delivery' ? fee : 0;
  const total = price + feeApplied;

  // ₩
  const fmt = (n, withWon = false) =>
    (withWon ? '₩ ' : '') + n.toLocaleString('ko-KR');

  // DOM 요소 모음
  const els = {
    mainPrice: document.getElementById('mainPrice'),
    feeExtra: document.getElementById('feeExtra'),
    rawPrice: document.getElementById('rawPrice'),
    rawFee: document.getElementById('rawFee'),
    totalPrice: document.getElementById('totalPrice'),
  };

  // 메인 가격
  if (els.mainPrice) els.mainPrice.textContent = fmt(price, true);

  // 배송비 안내
  if (els.feeExtra) {
    if (trade === 'delivery') {
      els.feeExtra.textContent = `(${fmt(fee, true)})`;
      els.feeExtra.style.display = 'block';
    } else {
      els.feeExtra.style.display = 'none';
    }
  }

  // 총 금액 관련
  if (els.rawPrice) els.rawPrice.textContent = fmt(price);
  if (els.rawFee) els.rawFee.textContent = fmt(feeApplied);
  if (els.totalPrice) els.totalPrice.textContent = fmt(total, true);

  const hintEl = document.querySelector('.total .hint');
    if (hintEl) {
        // 직거래이면 힌트 숨기기
        if (feeApplied === 0) {
            hintEl.style.display = 'none';
        } else {
            hintEl.style.display = 'inline';
        }
    }

})();

// 2) == heart 기능 ===

function getItemId() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
}

function showHeart() {
    const itemId = getItemId();
    
    $.ajax({
        type: 'GET',
        url: `/show_heart/${itemId}/`,data: {},
        success: function (response) {
            if (response.my_heart && response.my_heart['interested'] == 'Y') {
                $("#heart").css("color","#155724");
                $("#heart").attr("onclick","unlike()");
            } else {
                $("#heart").css("color","#757575");
                $("#heart").attr("onclick","like()");
            }
        },
        error: function(request, status, error) {
            console.log("Error checking heart status:", error);
            $("#heart").css("color","grey");
            $("#heart").attr("onclick","like()");
        }
    });
}

function like() {
    const itemId = getItemId();

    $.ajax({
        type: 'POST',
        url: `/like/${itemId}/`,
        data: { interested : "Y" },
        success: function (response) {
            alert(response['msg']);
            window.location.reload();
        },
        error: function(request, status, error) {
            if (request.status === 401) {
                alert('좋아요를 하려면 로그인이 필요합니다.');
                window.location.href = '/login';
            } else {
                alert('오류가 발생했습니다.');
            }
        }
    });
}
function unlike() {
    const itemId = getItemId();

    $.ajax({
        type: 'POST',
        url: `/unlike/${itemId}/`,
        data: { interested : "N" },
        success: function (response) {
            alert(response['msg']);
            window.location.reload();
        },
        error: function(request, status, error) {
            if (request.status === 401) {
                alert('로그인이 필요합니다.');
                window.location.href = '/login';
            } else {
                alert('오류가 발생했습니다.');
            }
        }
    });
}
$(document).ready(function () {
    showHeart();
});

// 3) === 판매 완료 기능 === 
// Y = 구매 가능, N = 구매 불가능 = 판매 완료
document.addEventListener('DOMContentLoaded', () => {
  const buyBtn = document.querySelector('.buy-btn');
  const reviewBtn = document.querySelector('.reg_review-btn');

  if (!buyBtn) return;

  const itemId = buyBtn.dataset.itemId;
  let sale = buyBtn.dataset.sale;   // 'Y' or 'N'

  function setSoldOut() {
    buyBtn.textContent = '판매 완료';
    buyBtn.style.backgroundColor = '#757575';
    buyBtn.disabled = true; // 클릭 못하게
    buyBtn.style.opacity = "0.5";
    buyBtn.style.cursor = "not-allowed";
    reviewBtn.style.display = "inline-block";
  }

  // 이미 판매 완료인 상태로 들어온 경우
  if (sale === 'N') {
    setSoldOut();
    return;
  }
  buyBtn.addEventListener('click', () => {
  
  fetch(`/purchase/${itemId}/`, {
    method: 'POST',
  })
    .then(res => {
      // (1) 로그인 안 한 경우
      if (res.status === 401) {
        alert('상품을 구매하려면 로그인이 필요합니다.');
        const next = encodeURIComponent(location.pathname + location.search);
        window.location.href = `/login`;
        return null;
      }
      // (2) 로그인 정상 + 구매 가능
      return res.json();
    })
    .then(data => {
      if (!data) return;

      // 확인창
      const yes = confirm("구매하시겠습니까?");
      if (!yes) return;

      alert(data.msg || "구매 완료!");
      sale = 'N';
      setSoldOut();
    })
    .catch(err => {
      console.error(err);
      alert('오류가 발생했습니다.');
    });
  });
});

// 4) === 이미지 슬라이더 ===
document.addEventListener("DOMContentLoaded", () => {

    const imageDataElement = document.getElementById("image-list");
    const imageList = JSON.parse(imageDataElement.dataset.images);

    let index = 0;

    const imgTag = document.getElementById("detail-img");
    const pager = document.getElementById("pager");
    const nextBtn = document.getElementById("next-btn");
    const prevBtn = document.getElementById("prev-btn");

    // 이미지 1장일 때 = 좌우 화살표 비활성화
    if (imageList.length <= 1) {
        nextBtn.disabled = true;
        prevBtn.disabled = true;

        nextBtn.style.opacity = "0";
        prevBtn.style.opacity = "0";

        nextBtn.style.cursor = "default";
        prevBtn.style.cursor = "default";

        return;
    }

    // 이미지 2장부터 = 좌우 화살표버튼 활성화
    nextBtn.addEventListener("click", () => {
        index = (index + 1) % imageList.length;
        updateImage();
    });

    prevBtn.addEventListener("click", () => {
        index = (index - 1 + imageList.length) % imageList.length;
        updateImage();
    });

    function updateImage() {
        imgTag.src = "/static/images/" + imageList[index];
        pager.textContent = `${index + 1} / ${imageList.length}`;
    }

});