const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

document.addEventListener('click', () => {
  tooltipList.forEach(tooltip => tooltip.hide());
});

const processAllButton = document.getElementById('process-all');

function processAll() {
  if (!confirm('Todas as requisições não processadas serão submetidas. Deseja continuar?')) {
    return;
  }
  const allRows = document.querySelectorAll('tr.requisicao-rows');
  console.log(allRows)

  allRows.forEach(row => {
    const tr = row.closest('tr');
    if (tr) {
      console.log(tr);

      const processLink = tr.querySelector('#process-row');
      if (processLink) {
        processLink.click();
      }
    }
  });
}

if (processAllButton) {
  processAllButton.addEventListener('click', processAll);
}

// Toast Management
function initializeToasts() {
  const toastElList = document.querySelectorAll('.toast');
  const toastList = [...toastElList].map(toastEl => {
    // Create toast instance with custom options
    const toast = new bootstrap.Toast(toastEl, {
      autohide: true,
      delay: 5000
    });

    // Add fade out animation before hiding
    toastEl.addEventListener('hide.bs.toast', function () {
      this.classList.add('fade-out');
    });

    return toast;
  });

  // Show all toasts
  toastList.forEach(toast => {
    toast.show();
  });

  return toastList;
}

// Function to create dynamic toasts
function showToast(message, type = 'info', duration = 5000) {
  const toastContainer = document.querySelector('.toast-container') || createToastContainer();

  const toastHtml = `
    <div class="toast align-items-center border-0 text-bg-${type}" role="alert" aria-live="assertive" aria-atomic="true" data-bs-autohide="true" data-bs-delay="${duration}">
      <div class="d-flex">
        <div class="toast-body">
          ${getToastIcon(type)}
          ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
    </div>
  `;

  toastContainer.insertAdjacentHTML('beforeend', toastHtml);

  const newToast = toastContainer.lastElementChild;
  const toast = new bootstrap.Toast(newToast);

  // Remove toast element after it's hidden
  newToast.addEventListener('hidden.bs.toast', function () {
    this.remove();
  });

  toast.show();
  return toast;
}

// Helper function to create toast container if it doesn't exist
function createToastContainer() {
  const container = document.createElement('div');
  container.className = 'toast-container position-fixed top-0 end-0 p-3';
  container.style.zIndex = '9999';
  document.body.appendChild(container);
  return container;
}

// Helper function to get appropriate icon for toast type
function getToastIcon(type) {
  const icons = {
    'success': '<i class="bi bi-check-circle-fill me-2"></i>',
    'danger': '<i class="bi bi-exclamation-triangle-fill me-2"></i>',
    'error': '<i class="bi bi-exclamation-triangle-fill me-2"></i>',
    'warning': '<i class="bi bi-exclamation-circle-fill me-2"></i>',
    'info': '<i class="bi bi-info-circle-fill me-2"></i>',
    'primary': '<i class="bi bi-bell-fill me-2"></i>'
  };
  return icons[type] || icons['info'];
}

// Initialize toasts when DOM is loaded
document.addEventListener('DOMContentLoaded', function () {
  initializeToasts();
});

// Legacy support for existing message system
document.body.addEventListener("showMessage", function (evt) {
  const message = evt.detail.value;
  const type = evt.detail.type || 'info';
  showToast(message, type);
});

// Export functions for global access
window.showToast = showToast;
window.initializeToasts = initializeToasts;
