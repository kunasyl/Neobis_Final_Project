from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from . import models, services

sms_services = services.SMSServices()


class CreateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.User
        fields = ('first_name', 'last_name', 'birth_date', 'phone_number',)


class VerifyCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=4)

    def create(self, validated_data):
        phone_number = self.context.get('phone_number')
        user_id = self.context.get('user_id')
        actual_code = models.PhoneVerification.objects.get(phone_number=phone_number).code
        if validated_data.get('code') == actual_code:
            # verify user
            user = models.User.objects.get(id=user_id)
            user.is_verified = True
            user.save()

            # save phone_number
            profile = models.Profile.objects.get(user_id=user_id)
            profile.phone_number = phone_number
            profile.save()

        return {'code': actual_code}


class LoginSerializer(serializers.ModelSerializer):
    """
    Send SMS to phone number for verification
    """

    class Meta:
        model = models.PhoneVerification
        fields = '__all__'
        extra_kwargs = {
            'phone_number': {'required': True}
        }

    def create(self, validated_data):
        phone_number = validated_data.get('phone_number')
        msg_code = sms_services.send_message(phone=phone_number, message='Код для верификации')

        if msg_code:
            phone_ver = models.PhoneVerification.objects.create(phone_number=phone_number, code=msg_code)

            return phone_ver

        raise ValidationError("Ошибка при отправке SMS на номер телефона")


class VerifyCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=4)
    user_id = serializers.IntegerField()

    def create(self, validated_data):
        phone_number = self.context.get('phone_number')
        user_id = validated_data.get('user_id')
        actual_code = models.PhoneVerification.objects.get(phone_number=phone_number).code
        if validated_data.get('code') == actual_code:
            # verify user
            user = models.User.objects.get(id=user_id)
            user.is_verified = True
            user.save()

            # save phone_number
            profile = models.Profile.objects.get(user_id=user_id)
            profile.phone_number = phone_number
            profile.save()

        return {'code': actual_code}