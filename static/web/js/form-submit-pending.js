(function () {
  function bind() {
    document.querySelectorAll('form[data-submit-pending]').forEach(function (form) {
      form.addEventListener('submit', function () {
        form.querySelectorAll('button[type="submit"], input[type="submit"]').forEach(function (btn) {
          if (btn.disabled) return;
          btn.disabled = true;
          btn.setAttribute('aria-busy', 'true');
          var label = btn.getAttribute('data-pending-label');
          if (label && btn.tagName === 'BUTTON' && btn.dataset.origSubmitLabel === undefined) {
            btn.dataset.origSubmitLabel = btn.textContent;
            btn.textContent = label;
          }
        });
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', bind);
  } else {
    bind();
  }
})();
