import hashlib
import urllib.error
import urllib.request
from pathlib import Path

from django.conf import settings
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
                'Esta senha consta na lista local de senhas proibidas.',
                code='password_forbidden_list',
            )

    def get_help_text(self):
        return 'A senha informada não pode estar na lista de senhas proibidas.'