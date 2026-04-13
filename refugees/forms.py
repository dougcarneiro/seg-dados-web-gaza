from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.password_validation import password_validators_help_text_html
from django.core.validators import RegexValidator
from django.utils.safestring import mark_safe

from .models import Refugee, User

_TW_FIELD = (
    'mt-1 w-full rounded border border-gray-300 px-3 py-2 text-gray-900 shadow-sm '
    'focus:border-slate-600 focus:outline-none focus:ring-1 focus:ring-slate-600'
)
_TW_CHECK = 'rounded border-gray-300 text-slate-700 focus:ring-slate-600'
_TW_SELECT = _TW_FIELD


def _apply_widgets(form):
    for name, field in form.fields.items():
        w = field.widget
        if isinstance(w, forms.CheckboxInput):
            w.attrs.setdefault('class', _TW_CHECK)
        elif isinstance(w, forms.Select):
            w.attrs.setdefault('class', _TW_SELECT)
        elif isinstance(w, forms.Textarea):
            w.attrs.setdefault('class', _TW_FIELD)
            w.attrs.setdefault('rows', 3)
        else:
            w.attrs.setdefault('class', _TW_FIELD)


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'autocomplete': 'email'}),
    )
    error_messages = {
        **AuthenticationForm.error_messages,
        'invalid_login': 'Credenciais inválidas.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_widgets(self)


class SignUpForm(UserCreationForm):
    name = forms.CharField(label='Nome')
    address = forms.CharField(
        label='Endereço',
        widget=forms.Textarea(attrs={'rows': 2}),
    )
    age = forms.IntegerField(label='Idade', min_value=1, max_value=130)
    religion = forms.ChoiceField(label='Religião', choices=Refugee.Religion.choices)
    political_ideology = forms.ChoiceField(
        label='Ideologia política',
        choices=Refugee.Ideology.choices,
    )
    profession = forms.CharField(label='Profissão')
    number_of_children = forms.IntegerField(label='Número de filhos', min_value=0, max_value=50)
    income_before_war = forms.DecimalField(
        label='Renda familiar antes da guerra',
        max_digits=12,
        decimal_places=2,
        min_value=0,
    )
    education = forms.ChoiceField(
        label='Maior grau de formação escolar',
        choices=Refugee.Education.choices,
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('email',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.password_rules_tooltip_html = mark_safe(password_validators_help_text_html())
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
        self.order_fields(
            [
                'email',
                'password1',
                'password2',
                'name',
                'address',
                'age',
                'religion',
                'political_ideology',
                'profession',
                'number_of_children',
                'income_before_war',
                'education',
            ]
        )
        _apply_widgets(self)
        for _fname in ('password1', 'password2'):
            w = self.fields[_fname].widget
            cls = w.attrs.get('class', '')
            w.attrs['class'] = cls.replace('px-3', 'pl-3 pr-10', 1)
        for _name, fld in self.fields.items():
            fld.required = True
            w = fld.widget
            if isinstance(w, forms.HiddenInput):
                continue
            if isinstance(w, forms.CheckboxInput):
                continue
            w.attrs['required'] = True
            w.attrs.setdefault('aria-required', 'true')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Refugee.objects.create(
                user=user,
                name=self.cleaned_data['name'],
                address=self.cleaned_data['address'],
                age=self.cleaned_data['age'],
                religion=self.cleaned_data['religion'],
                political_ideology=self.cleaned_data['political_ideology'],
                profession=self.cleaned_data['profession'],
                number_of_children=self.cleaned_data['number_of_children'],
                income_before_war=self.cleaned_data['income_before_war'],
                education=self.cleaned_data['education'],
            )
        return user


class RefugiadoProfileForm(forms.ModelForm):
    two_factor_enabled = forms.BooleanField(
        label='Ativar autenticação em duas etapas por e-mail',
        required=False,
    )

    class Meta:
        model = Refugee
        fields = (
            'name',
            'address',
            'age',
            'religion',
            'political_ideology',
            'profession',
            'number_of_children',
            'income_before_war',
            'education',
        )
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self._user = user
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['two_factor_enabled'].initial = user.two_factor_enabled
        self.order_fields(
            [
                'name',
                'address',
                'age',
                'religion',
                'political_ideology',
                'profession',
                'number_of_children',
                'income_before_war',
                'education',
                'two_factor_enabled',
            ]
        )
        _apply_widgets(self)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self._user is not None:
            self._user.two_factor_enabled = self.cleaned_data.get('two_factor_enabled', False)
            if commit:
                self._user.save()
        if commit:
            instance.save()
        return instance


class OtpCodeForm(forms.Form):
    code = forms.CharField(
        label='Código de verificação',
        max_length=6,
        min_length=6,
        validators=[RegexValidator(r'^\d{6}$', 'Informe exatamente 6 dígitos.')],
        widget=forms.TextInput(attrs={'inputmode': 'numeric', 'autocomplete': 'one-time-code'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_widgets(self)
