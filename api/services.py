from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db.models.query_utils import Q
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework_simplejwt import tokens
from twilio.rest import Client
from django.conf import settings

import random
import string


from . import models


class SMSServices:
    """
    SMS send services for phone number verification
    """
    def send_message(self, phone, message):
        code = self.generate_code()
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body=f'{message}: {code}',
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone
            )
            if message:
                models.PhoneVerification.objects.create(phone_number=phone, code=code)
            return code
        except Exception as e:
            return '1111'

    @staticmethod
    def generate_code(length=4):
        code = ''.join(random.choice(string.digits) for i in range(length))
        return code
