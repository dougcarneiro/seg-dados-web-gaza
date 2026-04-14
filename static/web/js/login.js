(function () {
  if (typeof window.refugeesBindPasswordToggle !== 'function') return;
  const pw = document.getElementById('id_password');
  const btn = document.getElementById('login-toggle-password');
  window.refugeesBindPasswordToggle(pw, btn);
})();
