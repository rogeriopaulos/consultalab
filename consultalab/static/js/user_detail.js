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
