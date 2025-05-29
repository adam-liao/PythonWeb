document.addEventListener('DOMContentLoaded', function () {
    const accordionItems = document.querySelectorAll('.accordion-item');

    accordionItems.forEach(item => {
        const header = item.querySelector('.accordion-header');
        const content = item.querySelector('.accordion-content');

        header.addEventListener('click', () => {
            const isExpanded = header.getAttribute('aria-expanded') === 'true';

            // Close all other accordions (optional: remove if you want multiple open)
            // accordionItems.forEach(otherItem => {
            //     if (otherItem !== item) {
            //         otherItem.querySelector('.accordion-header').setAttribute('aria-expanded', 'false');
            //         const otherContent = otherItem.querySelector('.accordion-content');
            //         otherContent.setAttribute('hidden', '');
            //         otherContent.style.maxHeight = null;
            //     }
            // });

            if (isExpanded) {
                header.setAttribute('aria-expanded', 'false');
                content.setAttribute('hidden', '');
                content.style.maxHeight = null; // Collapse
            } else {
                header.setAttribute('aria-expanded', 'true');
                content.removeAttribute('hidden');
                content.style.maxHeight = content.scrollHeight + "px"; // Expand
            }
        });
    });
});
