from django.shortcuts import render

# Create your views here.
import openai
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import SymptomLog
from .serializers import SymptomLogSerializer
from users import decode_token
from django.contrib.auth.models import User

openai.api_key = settings.OPENAI_API_KEY

def get_user(request):
    token = request.headers.get("Authorization", "").split(" ")[1]
    payload = decode_token(token)
    return User.objects.filter(id=payload.get("id")).first() if payload else None

@api_view(['POST'])
def create_symptom(request):
    user = get_user(request)
    if not user:
        return Response({ "error": "Unauthorized" }, status=401)
    SymptomLog.objects.create(user=user, title=request.data['title'])
    return Response({ "message": "Symptom saved" })

@api_view(['GET'])
def history(request):
    user = get_user(request)
    if not user:
        return Response({ "error": "Unauthorized" }, status=401)
    logs = SymptomLog.objects.filter(user=user).order_by('-date_logged')
    return Response(SymptomLogSerializer(logs, many=True).data)

@api_view(['POST'])
def check_symptom(request):
    description = request.data.get("description", "")
    messages = [
        { "role": "system", "content": "You are a helpful medical assistant." },
        { "role": "user", "content": f"I have symptoms: {description}" }
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    content = response.choices[0].message["content"]
    return Response({ "suggestions": content.split("\n") })