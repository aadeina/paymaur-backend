from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import User
from .serializers import ChangePINSerializer, LogoutSerializer, RegisterSerializer, LoginSerializer, OTPVerifySerializer, ResetPINSerializer
from .otp_service import generate_otp, verify_otp

# -----------------------------
# Register — create account
# -----------------------------
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        generate_otp(user, "REGISTER")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "success": True,
            "message": "User registered. OTP sent for verification."
        }, status=status.HTTP_201_CREATED)


# -----------------------------
# Verify OTP — activate account
# -----------------------------
class VerifyOTPView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        code = serializer.validated_data["code"]
        purpose = serializer.validated_data["purpose"]

        user = User.objects.filter(phone=phone).first()
        if not user:
            return Response({"success": False, "message": "User not found"}, status=404)

        ok, msg = verify_otp(user, code, purpose)
        if not ok:
            return Response({"success": False, "message": msg}, status=400)

        if purpose == "REGISTER":
            user.is_verified = True
            user.save()

        return Response({"success": True, "message": msg}, status=200)


# -----------------------------
# Login — issue JWT
# -----------------------------
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]
        pin = serializer.validated_data["pin"]

        user = User.objects.filter(phone=phone).first()
        if not user:
            return Response({"success": False, "message": "Account not found"}, status=404)

        if not check_password(pin, user.password):
            return Response({"success": False, "message": "Invalid PIN"}, status=401)

        refresh = RefreshToken.for_user(user)
        return Response({
            "success": True,
            "message": "Login successful",
            "data": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "phone": user.phone,
                    "is_verified": user.is_verified,
                }
            }
        })

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "message": "Logged out successfully"})

class ChangePINView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePINSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "message": "PIN changed successfully"})

class ForgotPINStartView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone = request.data.get("phone")
        user = User.objects.filter(phone=phone).first()
        if not user:
            return Response({"success": False, "message": "User not found"}, status=404)

        generate_otp(user, "RESET_PIN")
        return Response({"success": True, "message": "OTP sent for PIN reset"})

class ForgotPINVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone = request.data.get("phone")
        code = request.data.get("code")

        user = User.objects.filter(phone=phone).first()
        if not user:
            return Response({"success": False, "message": "User not found"}, status=404)

        ok, msg = verify_otp(user, code, "RESET_PIN")
        if not ok:
            return Response({"success": False, "message": msg}, status=400)

        return Response({"success": True, "message": "OTP verified successfully"})

class ResetPINView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResetPINSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"success": True, "message": "PIN reset successfully"})
