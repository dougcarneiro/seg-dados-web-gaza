from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('O e-mail é obrigatório.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superusuário exige is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superusuário exige is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField('e-mail', unique=True)
    two_factor_enabled = models.BooleanField('2FA por e-mail ativo', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'usuário'
        verbose_name_plural = 'usuários'


class Refugee(models.Model):
    class Religion(models.TextChoices):
        MUCULMANO = 'muculmano', 'Muçulmano'
        JUDEU = 'judeu', 'Judeu'
        CATOLICO = 'catolico', 'Católico'

    class Ideology(models.TextChoices):
        ESQUERDA = 'esquerda', 'Esquerda'
        DIREITA = 'direita', 'Direita'
        CENTRO = 'centro', 'Centro'

    class Education(models.TextChoices):
        FUNDAMENTAL = 'fundamental', 'Ensino fundamental'
        MEDIO = 'medio', 'Ensino médio'
        SUPERIOR = 'superior', 'Ensino superior'
        POS = 'pos', 'Pós-graduação'

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='refugee',
        verbose_name='usuário',
    )
    name = models.CharField('nome', max_length=255)
    address = models.TextField('endereço')
    age = models.PositiveSmallIntegerField('idade')
    religion = models.CharField('religião', max_length=20, choices=Religion.choices)
    political_ideology = models.CharField(
        'ideologia política',
        max_length=20,
        choices=Ideology.choices,
    )
    profession = models.CharField('profissão', max_length=255)
    number_of_children = models.PositiveSmallIntegerField('número de filhos', default=0)
    income_before_war = models.DecimalField(
        'renda familiar antes da guerra',
        max_digits=12,
        decimal_places=2,
    )
    education = models.CharField(
        'maior grau de formação escolar',
        max_length=20,
        choices=Education.choices,
    )

    class Meta:
        verbose_name = 'refugee'
        verbose_name_plural = 'refugees'

    def __str__(self):
        return self.name
