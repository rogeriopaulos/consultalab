document.body.addEventListener('closeModal', function (evt) {
  const modal = document.getElementById('modals-create-user');
  if (modal) {
    const closeButton = modal.querySelector('[data-bs-dismiss=modal]');
    if (closeButton) {
      closeButton.click();
    }
  }
});

document.body.addEventListener('showMessageCreatedUser', function (evt) {

  const data = evt.detail;
  if (data && data.message) {

    // Criar toast do Bootstrap 5
    const toastDiv = document.createElement('div');
    toastDiv.className = 'toast';
    toastDiv.setAttribute('role', 'alert');
    toastDiv.setAttribute('aria-live', 'assertive');
    toastDiv.setAttribute('aria-atomic', 'true');

    // Definir classe de cor baseada no tipo
    const toastClass = data.type === 'danger' ? 'text-bg-danger' :
                      data.type === 'warning' ? 'text-bg-warning' :
                      data.type === 'info' ? 'text-bg-info' : 'text-bg-success';
    toastDiv.classList.add(toastClass);

    toastDiv.innerHTML = `
      <div class="toast-header">
        <strong class="me-auto">Sistema</strong>
        <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
      </div>
      <div class="toast-body">
        ${data.message}
      </div>
    `;

    // Encontrar ou criar container de toasts
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.id = 'toast-container';
      toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
      toastContainer.style.zIndex = '1055';
      document.body.appendChild(toastContainer);
    }

    // Inserir toast no container
    toastContainer.appendChild(toastDiv);

    // Inicializar e mostrar o toast
    const toast = new bootstrap.Toast(toastDiv, {
      autohide: true,
      delay: 5000
    });
    toast.show();

    // Remover toast do DOM após ser ocultado
    toastDiv.addEventListener('hidden.bs.toast', () => {
      toastDiv.remove();
    });
  } else {
  }
});

// Verificar se HTMX está carregado e se os triggers estão funcionando
document.addEventListener('DOMContentLoaded', function() {

  // Listener para debug de todos os triggers HTMX
  if (typeof htmx !== 'undefined') {
    htmx.on('htmx:trigger', function(evt) {
    });
  }
});
