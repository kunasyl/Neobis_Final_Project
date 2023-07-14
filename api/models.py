from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):

    def create_user(self, first_name, phone):
        """
        Создает и возвращает пользователя.
        """
        if first_name is None:
            raise TypeError('Users must have a name.')
        if phone is None:
            raise TypeError('Users must have a phone.')

        # user = self.model(username=username, email=self.normalize_email(email))
        user = self.model(first_name=first_name, phone=phone)
        user.save()

        return user

    def create_superuser(self, first_name, phone):
        """
        Создает и возвращет пользователя с привилегиями суперадмина.
        """
        if phone is None:
            raise TypeError('Superusers must have a password.')
        if first_name is None:
            raise TypeError('Superusers must have a name.')

        user = self.create_user(first_name, phone)
        user.is_superuser = True
        user.is_staff = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(unique=True, max_length=255, verbose_name=_('Имя'))
    last_name = models.CharField(null=True, blank=True, max_length=255, verbose_name=_('Фамилия'))
    birth_date = models.DateField(verbose_name=_('День рождения'))
    phone_number = PhoneNumberField(null=True, blank=True, unique=True, verbose_name=_('Номер телефона'))

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'first_name'

    objects = UserManager()

    class Meta:
        ordering = ('-created_at',)
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __str__(self):
        return self.name

    @property
    def token(self):
        return self._generate_jwt_token()

    def _generate_jwt_token(self):
        """
        Генерирует веб-токен JSON, в котором хранится идентификатор этого
        пользователя, срок действия токена составляет 1 день от создания
        """
        dt = datetime.now() + timedelta(days=1)

        token = jwt.encode({
            'id': self.pk,
            'exp': int(dt.strftime('%s'))
        }, settings.SECRET_KEY, algorithm='HS256')

        # return token.decode('utf-8')
        return token


class PhoneVerification(models.Model):
    phone_number = PhoneNumberField(null=True, blank=True, unique=True, verbose_name=_('Номер телефона'))
    code = models.CharField(null=True, blank=True, max_length=4, verbose_name=_('Код'))
