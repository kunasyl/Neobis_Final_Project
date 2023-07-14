from rest_framework.response import Response
from django.http import HttpResponse, HttpResponseNotFound
from rest_framework.exceptions import NotFound
import json
from django.contrib import messages
from django.shortcuts import render, redirect
from rest_framework.decorators import action
from django.urls import reverse
from rest_framework import status
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from . import serializers, services, repos, permissions, models
from users.tokens import account_activation_token

auth_services = services.AuthServices()


class RegisterView(APIView):
    repos = repos.AuthRepos()

    @swagger_auto_schema(method='POST', request_body=serializers.CreateUserSerializer())
    @action(detail=False, methods=['POST'])
    def post(self, request, *args, **kwargs):
        serializer = serializers.CreateUserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Send SMS to phone number for login.
    """
    user_model = models.User
    repos = repos.ProfileRepos()

    @swagger_auto_schema(method='POST', request_body=serializers.LoginSerializer())
    @action(detail=False, methods=['POST'])
    def post(self, request):
        serializer = serializers.LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PhoneNumberVerificationView(APIView):
    """
    Check verification code sent to phone number
    """
    permission_classes = [permissions.IsAuthorizedPermission]

    @swagger_auto_schema(method='POST', request_body=serializers.VerifyCodeSerializer())
    @action(detail=False, methods=['POST'])
    def post(self, request, phone_number):
        context = {
            'phone_number': phone_number,
            'user_id': request.user.id
        }
        serializer = serializers.VerifyCodeSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
