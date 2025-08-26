function copyToClipboard(elementId) {
  const element = document.getElementById(elementId);
  element.select();
  element.setSelectionRange(0, 99999);

  navigator.clipboard.writeText(element.value).then(() => {
    // Feedback visual no botão
    const button = element.nextElementSibling;
    const originalIcon = button.innerHTML;
    button.innerHTML = '<i class="bi bi-check"></i>';
    button.classList.add('btn-success');
    button.classList.remove('btn-outline-secondary');

    // Criar notificação toast
    showCopyFeedback();

    setTimeout(() => {
      button.innerHTML = originalIcon;
      button.classList.remove('btn-success');
      button.classList.add('btn-outline-secondary');
    }, 2000);
  }).catch(err => {
    console.error('Erro ao copiar:', err);
    // Fallback para dispositivos que não suportam clipboard API
    element.select();
    document.execCommand('copy');
    showCopyFeedback();
  });
}

function showCopyFeedback() {
  // Remove notificação existente se houver
  const existingFeedback = document.querySelector('.copy-feedback');
  if (existingFeedback) {
    existingFeedback.remove();
  }

  // Criar nova notificação
  const feedback = document.createElement('div');
  feedback.className = 'copy-feedback';
  feedback.innerHTML = '<i class="bi bi-check-circle me-2"></i>Chave copiada!';
  document.body.appendChild(feedback);

  // Mostrar com animação
  setTimeout(() => feedback.classList.add('show'), 100);

  // Remover após 3 segundos
  setTimeout(() => {
    feedback.classList.remove('show');
    setTimeout(() => feedback.remove(), 300);
  }, 3000);
}

// Melhorar a experiência do campo de código
document.addEventListener('DOMContentLoaded', function () {
  const codeInput = document.querySelector('input[maxlength="6"]');
  if (codeInput) {
    // Formatação automática enquanto digita
    codeInput.addEventListener('input', function (e) {
      // Remove caracteres não numéricos
      this.value = this.value.replace(/\D/g, '');

      // Limita a 6 dígitos
      if (this.value.length > 6) {
        this.value = this.value.slice(0, 6);
      }
    });

    // Forçar entrada numérica no mobile
    codeInput.addEventListener('keydown', function (e) {
      // Permitir backspace, delete, tab, escape, enter, home, end, arrow keys
      if ([8, 9, 27, 13, 46, 35, 36, 37, 38, 39, 40].indexOf(e.keyCode) !== -1 ||
        // Permitir Ctrl+A, Ctrl+C, Ctrl+V, Ctrl+X
        (e.keyCode === 65 && e.ctrlKey === true) ||
        (e.keyCode === 67 && e.ctrlKey === true) ||
        (e.keyCode === 86 && e.ctrlKey === true) ||
        (e.keyCode === 88 && e.ctrlKey === true)) {
        return;
      }
      // Permitir apenas números (0-9)
      if ((e.shiftKey || (e.keyCode < 48 || e.keyCode > 57)) && (e.keyCode < 96 || e.keyCode > 105)) {
        e.preventDefault();
      }
    });

    // Auto-submit quando completar 6 dígitos (opcional)
    codeInput.addEventListener('input', function (e) {
      if (this.value.length === 6) {
        // Pequeno delay para melhor UX - destaca o botão de envio
        setTimeout(() => {
          const form = this.closest('form');
          if (form) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
              submitBtn.classList.add('pulse-animation');
              submitBtn.focus();
              setTimeout(() => submitBtn.classList.remove('pulse-animation'), 1000);
            }
          }
        }, 500);
      }
    });

    // Foco automático
    codeInput.focus();
  }
});
