(function () {
  function bindPasswordToggle(input, btn) {
    if (!input || !btn) return;
    const showEye = btn.querySelector('.js-pw-toggle-show');
    const hideEye = btn.querySelector('.js-pw-toggle-hide');
    if (!showEye || !hideEye) return;
    btn.addEventListener('click', function () {
      const reveal = input.type === 'password';
      input.type = reveal ? 'text' : 'password';
      btn.setAttribute('aria-pressed', reveal ? 'true' : 'false');
      btn.setAttribute('aria-label', reveal ? 'Ocultar senha' : 'Mostrar senha');
      showEye.classList.toggle('hidden', reveal);
      hideEye.classList.toggle('hidden', !reveal);
    });
  }
  window.refugeesBindPasswordToggle = bindPasswordToggle;
})();
