from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model, authenticate
from django.conf import settings
from rest_framework import status
import jwt
from datetime import datetime, timedelta

User = get_user_model()
SECRET_KEY = settings.SECRET_KEY

def create_jwt(user):
    payload = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_jwt(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

class SignupView(APIView):
    def post(self, request):
        data = request.data
        email = data.get("email")
        username = data.get("username")
        password = data.get("password")
        name = data.get("name")

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists."}, status=400)

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=name
        )

        token = create_jwt(user)
        return Response({"token": token}, status=201)

class LoginView(APIView):
    def post(self, request):
        data = request.data
        email = data.get("email")
        password = data.get("password")

        user_qs = User.objects.filter(email=email)
        if not user_qs.exists():
            return Response({"error": "User not found."}, status=404)

        user = authenticate(username=user_qs[0].username, password=password)
        if user:
            token = create_jwt(user)
            return Response({"token": token}, status=200)
        return Response({"error": "Invalid credentials."}, status=401)

class ProfileView(APIView):
    def get(self, request):
        auth_header = request.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "")
        decoded = decode_jwt(token)

        if not decoded:
            return Response({"error": "Invalid or expired token."}, status=401)

        return Response({
            "username": decoded["username"],
            "email": decoded["email"],
            "name": User.objects.get(username=decoded["username"]).first_name
        }, status=200)