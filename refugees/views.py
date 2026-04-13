import json
import time

import secrets
from django.conf import settings
from django.contrib.auth.password_validation import get_password_validators
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .forms import EmailAuthenticationForm, OtpCodeForm, RefugiadoProfileForm, SignUpForm
from .models import Refugee

_PASSWORD_PREVIEW_SKIP = 'refugees.validators.PwnedPasswordValidator'


@require_POST
def password_strength_preview(request):
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'ok': False, 'messages': ['Dados inválidos.']}, status=400)
    password = data.get('password', '') or ''
    email = (data.get('email') or '').strip()
    name = (data.get('name') or '').strip()
    fake = get_user_model()(
        email=email or 'placeholder@local.invalid',
        first_name=(name[:150] if name else ''),
    )
    config = [
        item
        for item in settings.AUTH_PASSWORD_VALIDATORS
        if item['NAME'] != _PASSWORD_PREVIEW_SKIP
    ]
    collected = []
    for validator in get_password_validators(config):
        try:
            validator.validate(password, fake)
        except ValidationError as exc:
            collected.extend(list(exc.messages))
    return JsonResponse({'ok': len(collected) == 0, 'messages': collected})


def home(request):
    return render(request, 'refugees/home.html')


@require_http_methods(['GET', 'POST'])
def signup(request):
    if request.user.is_authenticated:
        return redirect('refugees:profile')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cadastro criado. Entre com seu e-mail e senha.')
            return redirect('refugees:login')
    else:
        form = SignUpForm()
    return render(request, 'refugees/signup.html', {'form': form})


class EmailLoginView(LoginView):
    template_name = 'refugees/login.html'
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        if user.two_factor_enabled:
            code = f'{secrets.randbelow(1000000):06d}'
            self.request.session['pending_2fa_user_id'] = user.pk
            self.request.session['pending_2fa_hash'] = make_password(code)
            self.request.session['pending_2fa_expires'] = time.time() + 600
            send_mail(
                subject='Código de verificação (OTP)',
                message=f'Seu código de uso único: {code}\nVálido por 10 minutos.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
            messages.info(self.request, 'Enviamos um código para o seu e-mail.')
            return redirect('refugees:verify_otp')
        return super().form_valid(form)


class AppLogoutView(LogoutView):
    next_page = '/'


@require_http_methods(['GET', 'POST'])
def verify_otp(request):
    uid = request.session.get('pending_2fa_user_id')
    if uid is None:
        messages.error(request, 'Não há verificação pendente.')
        return redirect('refugees:login')
    if request.method == 'POST':
        form = OtpCodeForm(request.POST)
        if form.is_valid():
            expires = request.session.get('pending_2fa_expires', 0)
            if time.time() > expires:
                for key in ('pending_2fa_user_id', 'pending_2fa_hash', 'pending_2fa_expires'):
                    request.session.pop(key, None)
                messages.error(request, 'O código expirou. Faça login novamente.')
                return redirect('refugees:login')
            submitted = form.cleaned_data['code'].strip()
            stored_hash = request.session.get('pending_2fa_hash')
            if stored_hash and check_password(submitted, stored_hash):
                user = get_user_model().objects.get(pk=uid)
                for key in ('pending_2fa_user_id', 'pending_2fa_hash', 'pending_2fa_expires'):
                    request.session.pop(key, None)
                login(request, user)
                messages.success(request, 'Autenticação em duas etapas concluída.')
                return redirect(settings.LOGIN_REDIRECT_URL)
            messages.error(request, 'Código inválido.')
    else:
        form = OtpCodeForm()
    return render(request, 'refugees/verify_otp.html', {'form': form})


def _get_refugee_or_redirect(request):
    if request.user.is_staff:
        messages.info(
            request,
            'Contas de equipe usam o painel administrativo, não o cadastro de refugiado.',
        )
        return None
    try:
        return request.user.refugee
    except Refugee.DoesNotExist:
        messages.error(request, 'Não há cadastro de refugiado vinculado a esta conta.')
        return None


@login_required
def profile(request):
    ref = _get_refugee_or_redirect(request)
    if ref is None:
        return redirect('refugees:home')
    return render(request, 'refugees/profile_detail.html', {'refugee': ref})


@login_required
@require_http_methods(['GET', 'POST'])
def profile_edit(request):
    ref = _get_refugee_or_redirect(request)
    if ref is None:
        return redirect('refugees:home')
    if request.method == 'POST':
        form = RefugiadoProfileForm(request.POST, instance=ref, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cadastro atualizado.')
            return redirect('refugees:profile')
    else:
        form = RefugiadoProfileForm(instance=ref, user=request.user)
    return render(request, 'refugees/profile_form.html', {'form': form})


@login_required
def profile_delete_confirm(request):
    ref = _get_refugee_or_redirect(request)
    if ref is None:
        return redirect('refugees:home')
    return render(request, 'refugees/profile_delete_confirm.html', {'refugee': ref})


@login_required
@require_POST
def profile_delete(request):
    ref = _get_refugee_or_redirect(request)
    if ref is None:
        return redirect('refugees:home')
    uid = request.user.pk
    logout(request)
    get_user_model().objects.filter(pk=uid).delete()
    messages.success(request, 'Sua conta e cadastro foram removidos.')
    return redirect('refugees:home')
