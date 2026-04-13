(function () {
  const cfg = window.REFUGEES_SIGNUP;
  const url = cfg && cfg.passwordPreviewUrl;
  const pw = document.getElementById('id_password1');
  const pw2 = document.getElementById('id_password2');
  const emailEl = document.getElementById('id_email');
  const nameEl = document.getElementById('id_name');
  const icon1 = document.getElementById('signup-password-live-icon');
  const err1 = document.getElementById('signup-password-live-errors');
  const icon2 = document.getElementById('signup-password2-live-icon');
  const msg2 = document.getElementById('signup-password2-live-msg');
  const submitBtn = document.getElementById('signup-submit-btn');
  if (!url || !pw || !pw2 || !icon1 || !err1 || !icon2 || !msg2 || !submitBtn) return;

  let timer = null;
  let reqId = 0;
  let passwordRemoteOk = false;
  let passwordRemotePending = false;

  const FIELD_IDS = [
    'id_email',
    'id_password1',
    'id_password2',
    'id_name',
    'id_address',
    'id_age',
    'id_religion',
    'id_political_ideology',
    'id_profession',
    'id_number_of_children',
    'id_income_before_war',
    'id_education',
  ];

  function csrf() {
    const el = document.querySelector('[name=csrfmiddlewaretoken]');
    return el ? el.value : '';
  }
  function esc(s) {
    const d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  const svgCheck =
    '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-emerald-600" viewBox="0 0 20 20" fill="currentColor" focusable="false" aria-hidden="true"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" /></svg>';
  const svgSpin =
    '<svg class="h-5 w-5 animate-spin text-gray-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>';
  const svgX =
    '<svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>';

  function allRequiredFilled() {
    for (let i = 0; i < FIELD_IDS.length; i++) {
      const el = document.getElementById(FIELD_IDS[i]);
      if (!el || !String(el.value || '').trim()) return false;
    }
    return true;
  }

  function emailOk() {
    const v = (emailEl && emailEl.value.trim()) || '';
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
  }

  function ageOk() {
    const el = document.getElementById('id_age');
    if (!el) return false;
    const n = parseInt(el.value, 10);
    return !isNaN(n) && n >= 1 && n <= 130;
  }

  function childrenOk() {
    const el = document.getElementById('id_number_of_children');
    if (!el) return false;
    const n = parseInt(el.value, 10);
    return !isNaN(n) && n >= 0 && n <= 50;
  }

  function incomeOk() {
    const el = document.getElementById('id_income_before_war');
    if (!el) return false;
    const n = parseFloat(String(el.value).replace(',', '.'));
    return !isNaN(n) && n >= 0;
  }

  function passwordsMatch() {
    return pw.value.length > 0 && pw.value === pw2.value;
  }

  function password2State() {
    const a = pw.value;
    const b = pw2.value;
    if (!b) {
      return 'empty';
    }
    if (a !== b) {
      return 'mismatch';
    }
    return 'match';
  }

  function setClientError(fieldId, msg) {
    const p = document.getElementById(fieldId + '-client-error');
    if (!p) return;
    if (msg) {
      p.textContent = msg;
      p.classList.remove('hidden');
    } else {
      p.textContent = '';
      p.classList.add('hidden');
    }
  }

  function refreshClientError(fieldId) {
    const el = document.getElementById(fieldId);
    if (!el) return;
    const v = String(el.value || '').trim();
    let msg = '';
    if (!v) {
      msg = 'Preencha este campo.';
    } else if (fieldId === 'id_email' && !emailOk()) {
      msg = 'Informe um e-mail válido.';
    } else if (fieldId === 'id_age' && !ageOk()) {
      msg = 'Informe uma idade entre 1 e 130.';
    } else if (fieldId === 'id_number_of_children' && !childrenOk()) {
      msg = 'Informe um número entre 0 e 50.';
    } else if (fieldId === 'id_income_before_war' && !incomeOk()) {
      msg = 'Informe um valor numérico maior ou igual a zero.';
    }
    setClientError(fieldId, msg);
  }

  function refreshPassword1ClientError() {
    if (!pw.value.trim()) {
      setClientError('id_password1', 'Preencha este campo.');
    } else {
      setClientError('id_password1', '');
    }
  }

  function refreshPassword2ClientError() {
    if (!pw2.value.trim()) {
      setClientError('id_password2', 'Preencha este campo.');
    } else {
      setClientError('id_password2', '');
    }
  }

  function updatePassword2Ui() {
    const st = password2State();
    if (st === 'empty') {
      icon2.innerHTML = '';
      msg2.textContent = '';
      msg2.removeAttribute('class');
      msg2.className = 'mt-1 min-h-[1.25rem] text-sm';
      return;
    }
    if (st === 'mismatch') {
      icon2.innerHTML = svgX;
      msg2.textContent = 'As senhas não coincidem.';
      msg2.className = 'mt-1 min-h-[1.25rem] text-sm text-red-600';
      return;
    }
    icon2.innerHTML = svgCheck;
    msg2.textContent = '';
    msg2.className = 'mt-1 min-h-[1.25rem] text-sm';
  }

  function updateSubmitEnabled() {
    updatePassword2Ui();
    const base =
      allRequiredFilled() &&
      emailOk() &&
      ageOk() &&
      childrenOk() &&
      incomeOk() &&
      !passwordRemotePending &&
      passwordRemoteOk &&
      passwordsMatch();
    submitBtn.disabled = !base;
  }

  function runPasswordPreview() {
    const p = pw.value;
    if (!p) {
      icon1.innerHTML = '';
      err1.innerHTML = '';
      passwordRemoteOk = false;
      passwordRemotePending = false;
      updateSubmitEnabled();
      refreshPassword1ClientError();
      return;
    }
    const myReq = ++reqId;
    passwordRemotePending = true;
    icon1.innerHTML = svgSpin;
    err1.innerHTML = '';
    updateSubmitEnabled();
    fetch(url, {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrf(),
      },
      body: JSON.stringify({
        password: p,
        email: emailEl ? emailEl.value : '',
        name: nameEl ? nameEl.value : '',
      }),
    })
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        if (myReq !== reqId) return;
        passwordRemotePending = false;
        passwordRemoteOk = !!data.ok;
        if (data.ok) {
          icon1.innerHTML =
            '<span role="img" aria-label="Senha atende às regras locais; Have I Been Pwned ao enviar." title="Senha ok; HIBP ao enviar.">' +
            svgCheck +
            '</span>';
          err1.innerHTML = '';
        } else {
          icon1.innerHTML = '';
          const msgs = data.messages || [];
          err1.innerHTML =
            '<ul class="list-disc space-y-1 pl-5 text-red-600">' +
            msgs
              .map(function (m) {
                return '<li>' + esc(m) + '</li>';
              })
              .join('') +
            '</ul>';
        }
        updateSubmitEnabled();
        refreshPassword1ClientError();
      })
      .catch(function () {
        if (myReq !== reqId) return;
        passwordRemotePending = false;
        passwordRemoteOk = false;
        icon1.innerHTML = '';
        err1.innerHTML =
          '<p class="text-red-600">Não foi possível verificar agora. Tente de novo.</p>';
        updateSubmitEnabled();
        refreshPassword1ClientError();
      });
  }

  function schedulePreview() {
    clearTimeout(timer);
    timer = setTimeout(runPasswordPreview, 350);
  }

  pw.addEventListener('input', function () {
    passwordRemoteOk = false;
    schedulePreview();
    refreshPassword1ClientError();
    updateSubmitEnabled();
  });
  pw.addEventListener('blur', function () {
    clearTimeout(timer);
    runPasswordPreview();
    refreshPassword1ClientError();
  });

  pw2.addEventListener('input', function () {
    refreshPassword2ClientError();
    updateSubmitEnabled();
  });
  pw2.addEventListener('blur', function () {
    refreshPassword2ClientError();
    updateSubmitEnabled();
  });

  function bindRevalidate(el) {
    if (!el) return;
    const fid = el.id;
    el.addEventListener('input', function () {
      passwordRemoteOk = false;
      if (pw.value) schedulePreview();
      refreshClientError(fid);
      updateSubmitEnabled();
    });
    el.addEventListener('blur', function () {
      if (pw.value) runPasswordPreview();
      refreshClientError(fid);
      updateSubmitEnabled();
    });
  }
  bindRevalidate(emailEl);
  bindRevalidate(nameEl);

  FIELD_IDS.forEach(function (id) {
    const el = document.getElementById(id);
    if (!el || el === pw || el === pw2) return;
    const ev = el.tagName === 'SELECT' ? 'change' : 'input';
    el.addEventListener(ev, function () {
      refreshClientError(id);
      updateSubmitEnabled();
    });
    el.addEventListener('blur', function () {
      refreshClientError(id);
      updateSubmitEnabled();
    });
  });

  updateSubmitEnabled();
})();
