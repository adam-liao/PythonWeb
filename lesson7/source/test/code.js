document.addEventListener('DOMContentLoaded', function () {
    // 選取 DOM 元素
    const track = document.querySelector('.property-carousel-track');
    const cards = Array.from(track.children);
    const nextButton = document.querySelector('.next-arrow');
    const prevButton = document.querySelector('.prev-arrow');
    const dotsContainer = document.querySelector('.carousel-dots');

    let cardWidth; // 卡片寬度，將在 resize 時計算
    let cardsToShow; // 每次顯示的卡片數量
    let currentIndex = 0; // 目前顯示的第一張卡片的索引
    let totalCards = cards.length;
    let gap = 20; // 卡片間的 CSS gap 值，需與 CSS 同步

    // 根據視窗寬度決定顯示的卡片數量
    function getCardsToShow() {
        if (window.innerWidth <= 576) {
            return 1;
        } else if (window.innerWidth <= 992) {
            return 2;
        } else {
            return 3;
        }
    }

    // 設定卡片寬度，使它們能剛好填滿軌道容器
    function setCardDimensions() {
        cardsToShow = getCardsToShow();
        const trackContainerWidth = track.parentElement.offsetWidth; // 軌道容器的寬度

        // 在手機模式下，gap 可能會變小
        if (window.innerWidth <= 576) {
            gap = 10;
        } else {
            gap = 20;
        }

        // 計算每張卡片的理想寬度
        let idealCardWidth = (trackContainerWidth - (cardsToShow - 1) * gap) / cardsToShow;
        
        // 確保卡片寬度不小於 CSS 中設定的 min-width (近似值)
        let minCardWidthCss = 280; 
        if (window.innerWidth <= 992 && window.innerWidth > 576) minCardWidthCss = 260;
        // 手機上 min-width 較特殊，這裡用 idealCardWidth
        if (window.innerWidth > 576) {
             idealCardWidth = Math.max(idealCardWidth, minCardWidthCss);
        }


        cards.forEach(card => {
            card.style.width = `${idealCardWidth}px`;
        });
        // 更新 cardWidth 供 translate 使用
        cardWidth = cards[0] ? cards[0].offsetWidth : 0; // 使用實際渲染寬度
    }


    // 移動到指定的卡片索引
    function moveToSlide(targetIndex) {
        if (!cardWidth || totalCards === 0) return; // 如果沒有卡片寬度或卡片，則不執行

        // 計算位移量
        // targetIndex * (單張卡片寬度 + 間隙)
        const amountToMove = targetIndex * (cardWidth + gap);
        track.style.transform = `translateX(-${amountToMove}px)`;
        currentIndex = targetIndex;
        updateDots();
        updateArrows();
    }

    // 更新分頁點的狀態
    function updateDots() {
        if (!dotsContainer) return;
        dotsContainer.innerHTML = ''; // 清空現有點
        
        // 計算總共有多少「頁」
        const numPages = Math.ceil(totalCards / cardsToShow);
        // 如果只有一頁或沒有卡片，則不顯示分頁點
        if (numPages <= 1 && totalCards <= cardsToShow) { // 調整條件
             dotsContainer.style.display = 'none';
             return;
        }
        dotsContainer.style.display = 'block';


        for (let i = 0; i < numPages; i++) {
            const dot = document.createElement('button');
            dot.classList.add('dot');
            dot.setAttribute('aria-label', `跳至第 ${i + 1} 組房源`);
            if (i * cardsToShow === currentIndex || (i === Math.floor(currentIndex/cardsToShow))) { // 調整高亮邏輯
                dot.classList.add('active');
            }
            dot.addEventListener('click', () => {
                // 跳轉到這一頁的第一張卡片的索引
                moveToSlide(i * cardsToShow);
            });
            dotsContainer.appendChild(dot);
        }
    }

    // 更新箭頭按鈕的禁用狀態
    function updateArrows() {
        if (!prevButton || !nextButton) return;
        // 如果目前是第一張卡片，禁用「上一張」按鈕
        prevButton.disabled = currentIndex === 0;
        // 如果目前是最後一組可顯示的卡片，禁用「下一張」按鈕
        // (總卡片數 - 顯示卡片數) 是最後一組卡片開始的索引
        nextButton.disabled = currentIndex >= totalCards - cardsToShow;
    }

    // 初始化輪播
    function initializeCarousel() {
        setCardDimensions(); // 必須先設定卡片尺寸
        moveToSlide(0); // 然後移動到初始位置
        // updateDots(); // moveToSlide 已經包含 updateDots
        // updateArrows(); // moveToSlide 已經包含 updateArrows
    }

    // 事件監聽
    nextButton.addEventListener('click', () => {
        // 移動到下一組卡片，但不要超過邊界
        const nextIndex = Math.min(currentIndex + cardsToShow, totalCards - cardsToShow);
        // 如果 cardsToShow 是 1，則一次移動一張
        const step = (cardsToShow === 1 && currentIndex < totalCards - 1) ? 1 : cardsToShow;
        moveToSlide(Math.min(currentIndex + step, totalCards - cardsToShow));
    });

    prevButton.addEventListener('click', () => {
        // 移動到上一組卡片，但不要超過邊界
        // 如果 cardsToShow 是 1，則一次移動一張
        const step = (cardsToShow === 1 && currentIndex > 0) ? 1 : cardsToShow;
        moveToSlide(Math.max(currentIndex - step, 0));
    });

    // 響應式調整：當視窗大小改變時，重新初始化輪播
    let resizeTimeout;
    window.addEventListener('resize', () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            const oldCardsToShow = cardsToShow;
            initializeCarousel();
            // 如果 cardsToShow 改變了，可能需要調整 currentIndex
            if (oldCardsToShow !== getCardsToShow()) {
                 // 嘗試保持目前視圖的中心，或跳回開頭
                 moveToSlide(0); // 簡單起見，跳回開頭
            } else {
                 moveToSlide(currentIndex); // 維持目前索引
            }
        }, 250); // 防抖動，延遲250毫秒執行
    });

    // 執行初始化
    initializeCarousel();
});