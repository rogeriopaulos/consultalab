// Gerenciar classes ativas das abas
document.addEventListener('click', function (e) {
  if (e.target.matches('.nav-link')) {
    // Remover classe active de todas as abas
    document.querySelectorAll('.nav-link').forEach(tab => {
      tab.classList.remove('active');
      tab.removeAttribute('aria-current');
    });

    // Adicionar classe active à aba clicada
    e.target.classList.add('active');
    e.target.setAttribute('aria-current', 'page');
  }
});

// Listener para mostrar mensagens de sucesso/erro
document.body.addEventListener('showMessageCreatedUser', function (evt) {
  const data = evt.detail;
  if (data && data.message) {
    // Criar toast do Bootstrap 5 com estilos padronizados do sistema
    const toastDiv = document.createElement('div');
    toastDiv.className = 'toast';
    toastDiv.setAttribute('role', 'alert');
    toastDiv.setAttribute('aria-live', 'assertive');
    toastDiv.setAttribute('aria-atomic', 'true');

    // Definir classe de cor e ícone baseado no tipo usando estilos do project.css
    const toastClass = data.type === 'danger' ? 'text-bg-danger' :
                      data.type === 'error' ? 'text-bg-error' :
                      data.type === 'warning' ? 'text-bg-warning' :
                      data.type === 'info' ? 'text-bg-info' :
                      data.type === 'primary' ? 'text-bg-primary' : 'text-bg-success';

    const iconClass = data.type === 'danger' || data.type === 'error' ? 'bi-x-circle-fill' :
                     data.type === 'warning' ? 'bi-exclamation-triangle-fill' :
                     data.type === 'info' ? 'bi-info-circle-fill' :
                     data.type === 'primary' ? 'bi-bell-fill' : 'bi-check-circle-fill';

    toastDiv.classList.add(toastClass);

    toastDiv.innerHTML = `
      <div class="toast-body">
        <i class="bi ${iconClass} me-2"></i>
        ${data.message}
      </div>
    `;

    // Encontrar ou criar container de toasts com estilo padronizado
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.id = 'toast-container';
      toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
      toastContainer.style.zIndex = '9999';
      document.body.appendChild(toastContainer);
    }

    // Inserir toast no container
    toastContainer.appendChild(toastDiv);

    // Inicializar e mostrar o toast com configurações padronizadas
    const toast = new bootstrap.Toast(toastDiv, {
      autohide: true,
      delay: 5000
    });
    toast.show();

    // Remover toast do DOM após ser ocultado
    toastDiv.addEventListener('hidden.bs.toast', () => {
      toastDiv.remove();
    });
  }
});
