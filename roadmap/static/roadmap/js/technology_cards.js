document.addEventListener('DOMContentLoaded', function () {

    const techItems = document.querySelectorAll('.tech-item');

    techItems.forEach(item => {
        const header = item.querySelector('.tech-header');
        const details = item.querySelector('.tech-details');

        header.addEventListener('click', function (e) {
            if (e.target.type === 'checkbox' || e.target.tagName === 'A') {
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

    const checkboxes = document.querySelectorAll('.tech-checkbox');

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            const techId = this.dataset.techId;
            const completed = this.checked;

            fetch('/toggle-progress/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    technology_id: techId,
                    completed: completed
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        updateProgressBars();
                        showNotification(data.message, 'success');
                    } else {
                        this.checked = !completed;
                        showNotification(data.message, 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    this.checked = !completed;
                    showNotification('Произошла ошибка', 'error');
                });
        });
    });

    function updateProgressBars() {
        const categoryCards = document.querySelectorAll('.category-card');

        categoryCards.forEach(card => {
            const checkboxes = card.querySelectorAll('.tech-checkbox');
            const total = checkboxes.length;
            const checked = Array.from(checkboxes).filter(cb => cb.checked).length;
            const percent = total > 0 ? Math.round((checked / total) * 100) : 0;

            const progressBar = card.querySelector('.progress-bar');
            const progressText = card.querySelector('.progress-text');

            if (progressBar) {
                progressBar.style.width = percent + '%';
                progressBar.setAttribute('aria-valuenow', percent);
                progressBar.textContent = percent + '%';
            }

            if (progressText) {
                progressText.textContent = `${checked} из ${total} изучено (${percent}%)`;
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
    }, 500);
});