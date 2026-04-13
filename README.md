# Cadastro de refugiados (Gaza) — Django

Aplicação web simples para registro e manutenção de dados de refugiados brasileiros, com autenticação por e-mail, política de senha reforçada e segundo fator por e-mail (OTP).

## Requisitos

- Python 3.12 (recomendado)
- Dependências em `requirements.txt`

## Configuração

1. Crie e ative um ambiente virtual.
2. Instale dependências: `pip install -r requirements.txt`
3. Copie `.env.example` para `.env` e preencha **todas** as variáveis. Não commite o `.env`.
4. Aplique migrações:

   ```bash
   python manage.py migrate
   ```

   Se o repositório não tiver migrações ainda, gere-as antes: `python manage.py makemigrations refugees` e depois `migrate`.

5. Crie um superusuário para acesso ao Django Admin (equipe): `python manage.py createsuperuser` (informe o e-mail quando solicitado).
6. Execute o servidor: `python manage.py runserver`

### Variáveis de ambiente (`.env`)

| Variável | Descrição |
|----------|-----------|
| `SECRET_KEY` | Chave secreta do Django (obrigatória, valor longo e aleatório). |
| `DEBUG` | `true` ou `false`. |
| `ALLOWED_HOSTS` | Hosts separados por vírgula (ex.: `127.0.0.1,localhost`). |
| `LANGUAGE_CODE` | Ex.: `pt-br`. |
| `TIME_ZONE` | Ex.: `America/Fortaleza`. |
| `SQLITE_PATH` | Caminho do arquivo SQLite relativo à raiz do projeto (ex.: `db.sqlite3`). |
| `EMAIL_BACKEND` | **Obrigatório.** Use `django.core.mail.backends.console.EmailBackend` para desenvolvimento (mensagens no **terminal do `runserver`**) ou `django.core.mail.backends.smtp.EmailBackend` para envio real (ex.: Mailtrap). |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Credenciais SMTP (só fazem efeito com backend SMTP; com `console`, são ignoradas). |
| `DEFAULT_FROM_EMAIL` | Remetente (ex.: `noreply@example.com`). |
| `HIBP_ENABLED` | `true` para ativar verificação opcional contra vazamentos (API Have I Been Pwned). |

Para **Mailtrap**, defina `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`, use host e credenciais do sandbox SMTP no painel do inbox e **reinicie** o servidor após alterar o `.env`. Se `EMAIL_BACKEND` continuar como `console`, o OTP aparece só no terminal — não chega ao Mailtrap nem ao e-mail do usuário.

## Uso

- **Público:** cadastro em `/signup/`, login em `/login/`, verificação OTP em `/verify-otp/` quando o 2FA estiver ativo, área logada em `/profile/` (detalhes), `/profile/edit/` (edição), `/profile/delete/` (fluxo de exclusão).
- **Equipe:** lista global de refugees em `/admin/` (superusuário).

### Cadastro (UX)

- Todos os campos são obrigatórios; rótulos marcados com `*` e validação auxiliar no navegador (mensagens ao sair do campo).
- A força da senha é conferida em tempo quase real via `POST` em `/signup/check-password/` (validadores locais; o validador HIBP só roda no envio do formulário, se estiver habilitado).
- O botão **Registrar** só habilita quando regras locais e confirmação de senha estão ok; login e cadastro desabilitam o botão de envio enquanto a requisição está em andamento (`static/web/js/form-submit-pending.js`).

### 2FA (OTP)

Novas contas são criadas com **autenticação em duas etapas ativa** por padrão (`two_factor_enabled` no `User`). Em **Editar cadastro** é possível **desligar** (ou religar) o 2FA. No login, com 2FA ativo e senha correta, um código de 6 dígitos é enviado por e-mail conforme `EMAIL_BACKEND` (SMTP ou texto no console).

---

## Atendimento aos requisitos funcionais (item 3)

### Autenticação com login e senha gravados localmente; login por e-mail

O modelo `refugees.User` estende `AbstractUser` com `USERNAME_FIELD = 'email'` e `email` único. O formulário `EmailAuthenticationForm` usa o campo `username` do Django como campo de e-mail. As credenciais são validadas por `EmailLoginView` (subclasse de `LoginView`); após sucesso, a sessão é criada com `login()` (ou inicia-se o fluxo OTP se o 2FA estiver ativo). Os dados persistem no SQLite via ORM (tabela do usuário customizado em `refugees`).

### Apenas hash da senha, nunca senha pura

O Django armazena no campo `password` uma string com algoritmo, salt e hash (por padrão PBKDF2). `UserCreationForm` e o admin usam o fluxo interno de `set_password` / `make_password`. A senha em claro não é gravada no banco.

### Força da senha e lista de senhas proibidas

Em `web_gaza/settings.py`, `AUTH_PASSWORD_VALIDATORS` inclui validadores nativos (comprimento mínimo 12, similaridade com dados do usuário, senhas comuns do Django, senha só numérica) mais `ForbiddenPasswordListValidator`, que lê `refugees/data/forbidden_passwords.txt`. Opcionalmente, `PwnedPasswordValidator` consulta a API k-anonymity do Have I Been Pwned quando `HIBP_ENABLED=true` no `.env` (falha de rede não impede o cadastro).

### Manutenção do próprio cadastro quando logado

Cada `Refugee` tem `OneToOneField` para `User`. As views `profile`, `profile_edit` e fluxo de exclusão carregam o registro com `user=request.user` (ou equivalente), de forma que só o titular altera nome, endereço, idade, religião, ideologia, profissão, filhos, renda e formação. O cadastro inicial é criado no mesmo fluxo do `SignUpForm`.

### 2FA por e-mail (OTP)

Se `two_factor_enabled` estiver ativo no usuário, após senha válida `EmailLoginView` gera um código numérico de 6 dígitos, guarda o **hash** na sessão com validade de 10 minutos, envia o código por `send_mail` e redireciona para `/verify-otp/`. Após validação com `check_password` sobre o código informado, chama-se `login()` e encerra-se a etapa pendente. O envio usa a configuração de e-mail do `.env` (SMTP ou backend de console).

---

## Estrutura principal

- `web_gaza/` — projeto Django e `settings.py` (somente leitura de variáveis de ambiente).
- `refugees/` — modelos `User` e `Refugee`, formulários, views, validadores de senha, admin, migrações em `refugees/migrations/`.
- `templates/refugees/` — páginas com Tailwind via CDN (layout simples); formulário de cadastro com partial `_signup_form_fields.html` e edição de perfil com `_profile_form_fields.html` (destaque do 2FA).
- `static/web/js/` — `tailwind-config.js`, `signup.js` (pré-validação de senha e campos), `form-submit-pending.js` (estado de envio nos formulários).
