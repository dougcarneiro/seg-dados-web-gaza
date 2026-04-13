# Cadastro de refugiados (Gaza) — Django

Aplicação web simples para registro e manutenção de dados de refugiados brasileiros, com autenticação por e-mail, política de senha reforçada e segundo fator opcional por e-mail (OTP).

## Requisitos

- Python 3.12 (recomendado)
- Dependências em `requirements.txt`

## Configuração

1. Crie e ative um ambiente virtual.
2. Instale dependências: `pip install -r requirements.txt`
3. Copie `.env.example` para `.env` e preencha **todas** as variáveis. Não commite o `.env`.
4. Gere e aplique migrações (não há arquivos de migração versionados neste repositório):

   ```bash
   python manage.py makemigrations refugees
   python manage.py migrate
   ```

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
| `EMAIL_BACKEND` | Ex.: `django.core.mail.backends.console.EmailBackend` (OTP no terminal) ou SMTP do Mailtrap. |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USE_TLS`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | Credenciais SMTP (Mailtrap: painel do inbox → SMTP). |
| `DEFAULT_FROM_EMAIL` | Remetente (ex.: `noreply@example.com`). |
| `HIBP_ENABLED` | `true` para ativar verificação opcional contra vazamentos (API Have I Been Pwned). |

Para **Mailtrap**, use o host e as credenciais do sandbox SMTP no `.env` e defina `EMAIL_BACKEND` para `django.core.mail.backends.smtp.EmailBackend`.

## Uso

- **Público:** cadastro em `/cadastro/`, login em `/login/`, área logada em `/perfil/` (visualizar, editar, excluir conta e cadastro).
- **Equipe:** lista global de refugees em `/admin/` (superusuário).

### 2FA (OTP)

Com a conta já criada, em **Editar cadastro** marque a opção de autenticação em duas etapas. No próximo login, após a senha correta, um código de 6 dígitos é enviado por e-mail (ou exibido no console se `EMAIL_BACKEND` for o backend de console).

---

## Atendimento aos requisitos funcionais (item 3)

### Autenticação com login e senha gravados localmente; login por e-mail

O modelo `refugees.User` estende `AbstractUser` com `USERNAME_FIELD = 'email'` e `email` único. O formulário `EmailAuthenticationForm` usa o campo `username` do Django como campo de e-mail. As credenciais são validadas por `EmailLoginView` (subclasse de `LoginView`); após sucesso, a sessão é criada com `login()`. Os dados persistem no SQLite via ORM (tabela do usuário customizado em `refugees`).

### Apenas hash da senha, nunca senha pura

O Django armazena no campo `password` uma string com algoritmo, salt e hash (por padrão PBKDF2). `UserCreationForm` e o admin usam o fluxo interno de `set_password` / `make_password`. A senha em claro não é gravada no banco.

### Força da senha e lista de senhas proibidas

Em `web_gaza/settings.py`, `AUTH_PASSWORD_VALIDATORS` inclui validadores nativos (comprimento mínimo 12, similaridade com dados do usuário, senhas comuns do Django, senha só numérica) mais `ForbiddenPasswordListValidator`, que lê `refugees/data/forbidden_passwords.txt`. Opcionalmente, `PwnedPasswordValidator` consulta a API k-anonymity do Have I Been Pwned quando `HIBP_ENABLED=true` no `.env` (falha de rede não impede o cadastro).

### Manutenção do próprio cadastro quando logado

Cada `Refugiado` tem `OneToOneField` para `User`. As views `profile`, `profile_edit` e fluxo de exclusão carregam o registro com `user=request.user` (ou equivalente), de forma que só o titular altera nome, endereço, idade, religião, ideologia, profissão, filhos, renda e formação. O cadastro inicial é criado no mesmo fluxo do `SignUpForm`.

### 2FA por e-mail (OTP)

Se `two_factor_enabled` estiver ativo no usuário, após senha válida `EmailLoginView` gera um código numérico de 6 dígitos, guarda o **hash** na sessão com validade de 10 minutos, envia o código por `send_mail` e redireciona para `verificar-codigo/`. Após validação com `check_password` sobre o código informado, chama-se `login()` e encerra-se a etapa pendente. O envio usa apenas configuração de e-mail do `.env` (Mailtrap ou console).

---

## Estrutura principal

- `web_gaza/` — projeto Django e `settings.py` (somente leitura de variáveis de ambiente).
- `refugees/` — modelos `User` e `Refugiado`, formulários, views, validadores de senha, admin.
- `templates/refugees/` — páginas com Tailwind via CDN (layout simples).
