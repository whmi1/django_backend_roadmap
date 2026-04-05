document.addEventListener('DOMContentLoaded', function () {

    const techItems = document.querySelectorAll('.tech-item');
    techItems.forEach(item => {
        const header = item.querySelector('.tech-header');
        const details = item.querySelector('.tech-details');

        header.addEventListener('click', function (e) {
            if (e.target.closest('.tech-status-selector') || e.target.tagName === 'A') {
                return;
            }
            item.classList.toggle('expanded');
            if (item.classList.contains('expanded')) {
                details.style.maxHeight = details.scrollHeight + 'px';
            } else {
                details.style.maxHeight = '0';
            }
        });
    });

    const statusSelects = document.querySelectorAll('.tech-status');
    statusSelects.forEach(select => {
        select.addEventListener('change', function () {
            const techId = this.dataset.techId;
            const status = this.value;

            fetch('/update-progress/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    technology_id: techId,
                    status: status
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateProgressBars();
                    applyFilter();
                    showNotification(data.message, 'success');
                } else {
                    showNotification(data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Произошла ошибка', 'error');
            });
        });
    });

    const filterBtns = document.querySelectorAll('.filter-btn');
    let currentFilter = 'all';

    function applyFilter() {
        const techItemsAll = document.querySelectorAll('.tech-item');
        let visibleCount = 0;

        techItemsAll.forEach(item => {
            const select = item.querySelector('.tech-status');
            if (!select) {
                item.style.display = '';
                visibleCount++;
                return;
            }

            const status = select.value;
            
            if (currentFilter === 'all' || status === currentFilter) {
                item.style.display = '';
                visibleCount++;
            } else {
                item.style.display = 'none';
            }
        });

        const noResultsMsg = document.getElementById('no-results-message');
        if (noResultsMsg) {
            if (visibleCount === 0 && currentFilter !== 'all') {
                noResultsMsg.classList.remove('d-none');
            } else {
                noResultsMsg.classList.add('d-none');
            }
        }

        const categoryCards = document.querySelectorAll('.category-card');
        categoryCards.forEach(card => {
            const visibleItems = card.querySelectorAll('.tech-item[style="display: block;"], .tech-item[style=""]');
            let hasVisible = false;
            card.querySelectorAll('.tech-item').forEach(item => {
                if (item.style.display !== 'none') {
                    hasVisible = true;
                }
            });
            card.style.display = hasVisible ? '' : 'none';
        });
    }

    filterBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            filterBtns.forEach(b => b.classList.remove('active', 'btn-primary'));
            filterBtns.forEach(b => b.classList.add('btn-outline-secondary'));
            
            this.classList.remove('btn-outline-secondary');
            this.classList.add('active', 'btn-primary');
            
            currentFilter = this.dataset.filter;
            
            applyFilter();
        });
    });

    function updateProgressBars() {
        const categoryCards = document.querySelectorAll('.category-card');
        categoryCards.forEach(card => {
            const selects = card.querySelectorAll('.tech-status');
            const total = selects.length;
            let completed = 0;
            selects.forEach(select => {
                if (select.value === 'completed') completed++;
            });
            const percent = total > 0 ? Math.round((completed / total) * 100) : 0;
            const progressBar = card.querySelector('.progress-bar');
            const progressText = card.querySelector('.progress-text');
            if (progressBar) {
                progressBar.style.width = percent + '%';
                progressBar.setAttribute('aria-valuenow', percent);
                progressBar.textContent = percent + '%';
            }
            if (progressText) {
                progressText.textContent = `${completed} из ${total} изучено (${percent}%)`;
            }
        });
    }

    function showNotification(message, type) {
        console.log(message);
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    setTimeout(function() {
        updateProgressBars();
        applyFilter();
    }, 500);
});