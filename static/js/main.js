/**
 * KAES LIBRARY MANAGEMENT SYSTEM - CLIENT SCRIPT
 * Handles Theme Toggling, Charts, Interactive Stack (LIFO) & Queue (FIFO), and Toasts.
 */

document.addEventListener('DOMContentLoaded', function () {
    // 1. Theme Toggle Initialization
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const htmlElem = document.documentElement;
    const savedTheme = localStorage.getItem('kaes_theme') || 'light';
    htmlElem.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', function () {
            const currentTheme = htmlElem.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            htmlElem.setAttribute('data-theme', newTheme);
            localStorage.setItem('kaes_theme', newTheme);
            updateThemeIcon(newTheme);
            // Re-render charts with updated theme colors if on dashboard
            if (window.renderDashboardCharts) {
                window.renderDashboardCharts();
            }
        });
    }

    function updateThemeIcon(theme) {
        if (!themeToggleBtn) return;
        const icon = themeToggleBtn.querySelector('i');
        if (icon) {
            if (theme === 'dark') {
                icon.className = 'fas fa-sun text-warning';
            } else {
                icon.className = 'fas fa-moon text-primary';
            }
        }
    }

    // 2. Mobile Sidebar Toggle
    const sidebarToggleBtn = document.getElementById('sidebarToggleBtn');
    const appSidebar = document.querySelector('.app-sidebar');
    if (sidebarToggleBtn && appSidebar) {
        sidebarToggleBtn.addEventListener('click', function () {
            appSidebar.classList.toggle('show');
        });
    }

    // 3. Auto-show Bootstrap Toasts
    const toastElements = document.querySelectorAll('.toast');
    toastElements.forEach(function (toastEl) {
        const toast = new bootstrap.Toast(toastEl, { delay: 5000 });
        toast.show();
    });

    // 4. Global Toast Trigger Helper
    window.showToast = function (message, type = 'success') {
        const toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) return;

        const toastId = 'toast-' + Date.now();
        const bgClass = type === 'success' ? 'bg-success text-white' : (type === 'error' ? 'bg-danger text-white' : 'bg-primary text-white');
        const iconClass = type === 'success' ? 'fa-check-circle' : (type === 'error' ? 'fa-exclamation-triangle' : 'fa-info-circle');

        const toastHtml = `
            <div id="${toastId}" class="toast align-items-center ${bgClass} border-0 shadow-lg" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body d-flex align-items-center gap-2">
                        <i class="fas ${iconClass}"></i>
                        <div>${message}</div>
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;
        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        const newToastEl = document.getElementById(toastId);
        const toast = new bootstrap.Toast(newToastEl, { delay: 4500 });
        toast.show();
    };

    // 5. Interactive Stack AJAX Operations
    const ajaxStackPopBtn = document.getElementById('ajaxStackPopBtn');
    const ajaxStackPeekBtn = document.getElementById('ajaxStackPeekBtn');

    if (ajaxStackPopBtn) {
        ajaxStackPopBtn.addEventListener('click', function () {
            const csrfToken = getCookie('csrftoken');
            fetch('/returns-stack/api/pop/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    window.showToast(data.message, 'success');
                    // Refresh stack visual container
                    setTimeout(() => location.reload(), 800);
                } else {
                    window.showToast(data.message, 'error');
                }
            })
            .catch(err => {
                window.showToast("Error executing POP operation: " + err, 'error');
            });
        });
    }

    if (ajaxStackPeekBtn) {
        ajaxStackPeekBtn.addEventListener('click', function () {
            fetch('/returns-stack/api/peek/')
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    const top = data.peek_item;
                    const modalBody = `
                        <div class="p-3">
                            <div class="d-flex align-items-center gap-3 mb-3">
                                <div class="stat-icon purple"><i class="fas fa-layer-group"></i></div>
                                <div>
                                    <h5 class="mb-0 fw-bold">${top.book_title}</h5>
                                    <span class="badge bg-purple text-white">ISBN: ${top.book_isbn}</span>
                                </div>
                            </div>
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item d-flex justify-content-between px-0">
                                    <span class="text-muted">Returned By Student:</span>
                                    <span class="fw-semibold">${top.student_name} (${top.student_id})</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between px-0">
                                    <span class="text-muted">Return Timestamp:</span>
                                    <span class="fw-semibold">${top.pushed_at}</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between px-0">
                                    <span class="text-muted">Book Condition:</span>
                                    <span class="badge bg-success-subtle text-success">${top.condition}</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between px-0">
                                    <span class="text-muted">Stack Position:</span>
                                    <span class="fw-bold text-primary">TOP (LIFO - Next to be Popped & Reshelved)</span>
                                </li>
                            </ul>
                        </div>
                    `;
                    showDynamicModal("Peek Top Return Stack Item", modalBody);
                } else {
                    window.showToast(data.message, 'error');
                }
            });
        });
    }

    // 6. Interactive Queue AJAX Operations
    const ajaxQueueDequeueBtn = document.getElementById('ajaxQueueDequeueBtn');
    const ajaxQueuePeekBtn = document.getElementById('ajaxQueuePeekBtn');

    if (ajaxQueueDequeueBtn) {
        ajaxQueueDequeueBtn.addEventListener('click', function () {
            const csrfToken = getCookie('csrftoken');
            fetch('/requests-queue/api/dequeue/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'Content-Type': 'application/json'
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    window.showToast(data.message, 'success');
                    setTimeout(() => location.reload(), 800);
                } else {
                    window.showToast(data.message, 'error');
                }
            })
            .catch(err => {
                window.showToast("Error executing DEQUEUE operation: " + err, 'error');
            });
        });
    }

    if (ajaxQueuePeekBtn) {
        ajaxQueuePeekBtn.addEventListener('click', function () {
            fetch('/requests-queue/api/peek/')
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') {
                    const front = data.peek_item;
                    const modalBody = `
                        <div class="p-3">
                            <div class="d-flex align-items-center gap-3 mb-3">
                                <div class="stat-icon success"><i class="fas fa-users-line"></i></div>
                                <div>
                                    <h5 class="mb-0 fw-bold">Request ${front.request_id}</h5>
                                    <span class="badge bg-success text-white">HEAD OF QUEUE (FIFO Front)</span>
                                </div>
                            </div>
                            <ul class="list-group list-group-flush">
                                <li class="list-group-item d-flex justify-content-between px-0">
                                    <span class="text-muted">Requested Book:</span>
                                    <span class="fw-bold">${front.book_title}</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between px-0">
                                    <span class="text-muted">Requesting Student:</span>
                                    <span class="fw-semibold">${front.student_name} (${front.student_id})</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between px-0">
                                    <span class="text-muted">Enqueued Timestamp:</span>
                                    <span class="fw-semibold">${front.request_date}</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between px-0">
                                    <span class="text-muted">Current Book Copies:</span>
                                    <span class="fw-bold ${front.book_available > 0 ? 'text-success' : 'text-danger'}">${front.book_available} Available</span>
                                </li>
                                <li class="list-group-item d-flex justify-content-between px-0">
                                    <span class="text-muted">Queue Priority:</span>
                                    <span class="fw-bold text-success">Next student to be served on Dequeue</span>
                                </li>
                            </ul>
                        </div>
                    `;
                    showDynamicModal("Peek Front Request in Queue", modalBody);
                } else {
                    window.showToast(data.message, 'error');
                }
            });
        });
    }

    function showDynamicModal(title, bodyHtml) {
        let modalEl = document.getElementById('dynamicAppModal');
        if (!modalEl) {
            const modalMarkup = `
                <div class="modal fade" id="dynamicAppModal" tabindex="-1" aria-hidden="true">
                    <div class="modal-dialog modal-dialog-centered">
                        <div class="modal-content glass-panel border-0">
                            <div class="modal-header border-bottom border-light-subtle">
                                <h5 class="modal-title fw-bold" id="dynamicModalTitle"></h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body" id="dynamicModalBody"></div>
                            <div class="modal-footer border-0">
                                <button type="button" class="btn btn-secondary rounded-pill px-4" data-bs-dismiss="modal">Close</button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalMarkup);
            modalEl = document.getElementById('dynamicAppModal');
        }
        document.getElementById('dynamicModalTitle').innerText = title;
        document.getElementById('dynamicModalBody').innerHTML = bodyHtml;
        const bsModal = new bootstrap.Modal(modalEl);
        bsModal.show();
    }

    // CSRF helper
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
});
