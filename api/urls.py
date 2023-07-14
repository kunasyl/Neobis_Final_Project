from django.urls import path

from api.views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify_code/<str:phone_number>', PhoneNumberVerificationView.as_view(), name='verify_code'),
]
