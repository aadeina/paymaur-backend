from django.urls import path
from .views import (
    RegisterView, VerifyOTPView, LoginView, LogoutView,
    ChangePINView, ForgotPINStartView, ForgotPINVerifyView, ResetPINView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("auth/pin/change/", ChangePINView.as_view(), name="change-pin"),
    path("auth/pin/forgot/start/", ForgotPINStartView.as_view(), name="forgot-pin-start"),
    path("auth/pin/forgot/verify/", ForgotPINVerifyView.as_view(), name="forgot-pin-verify"),
    path("auth/pin/reset/", ResetPINView.as_view(), name="reset-pin"),
]
