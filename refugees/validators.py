import re
from pathlib import Path

from django.core.exceptions import ValidationError

_DATA_FILE = Path(__file__).resolve().parent / 'data' / 'forbidden_passwords.txt'


class ForbiddenPasswordListValidator:
    def __init__(self):
        self._forbidden = set()
        if _DATA_FILE.exists():
            for line in _DATA_FILE.read_text(encoding='utf-8').splitlines():
                entry = line.strip().lower()
                if entry and not entry.startswith('#'):
                    self._forbidden.add(entry)

    def validate(self, password, user=None):
        if password.lower() in self._forbidden:
            raise ValidationError(
                'Esta senha é considerada muito simples. Por favor, escolha uma senha mais forte.',
                code='password_forbidden_list',
            )

    def get_help_text(self):
        return 'A senha informada não pode estar na lista de senhas proibidas.'


class UppercaseLowercaseValidator:
    """Exige ao menos uma letra minúscula e uma maiúscula (ASCII a-z / A-Z)."""

    def validate(self, password, user=None):
        messages = []
        if not re.search(r'[a-z]', password):
            messages.append('A senha deve conter ao menos uma letra minúscula.')
        if not re.search(r'[A-Z]', password):
            messages.append('A senha deve conter ao menos uma letra maiúscula.')
        if messages:
            raise ValidationError(messages)

    def get_help_text(self):
        return (
            'Sua senha deve conter ao menos uma letra minúscula e ao menos uma letra maiúscula.'
        )


class AtLeastOneDigitValidator:
    """Exige ao menos um dígito decimal (0-9)."""

    def validate(self, password, user=None):
        if not re.search(r'\d', password):
            raise ValidationError(
                'A senha deve conter ao menos um caractere numérico.',
                code='password_no_digit',
            )

    def get_help_text(self):
        return 'Sua senha deve conter ao menos um caractere numérico (0–9).'


class SpecialCharacterValidator:
    """Exige ao menos um caractere que não seja letra ou dígito ASCII."""

    def validate(self, password, user=None):
        if not re.search(r'[^A-Za-z0-9]', password):
            raise ValidationError(
                'A senha deve conter ao menos um caractere especial (não alfanumérico).',
                code='password_no_special',
            )

    def get_help_text(self):
        return (
            'Sua senha deve conter ao menos um caractere especial '
            '(por exemplo: ! @ # $ % & *).'
        )