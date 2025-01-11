from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import CustomUser

@api_view(['POST'])
def user_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        return JsonResponse({'message': 'Login successful'}, status=200)
    return JsonResponse({'error': 'Invalid credentials'}, status=401)

@api_view(['POST'])
def user_signup(request):
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    if CustomUser.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Username already exists'}, status=400)
    user = CustomUser.objects.create_user(username=username, password=password, email=email)
    return JsonResponse({'message': 'User created successfully'}, status=201)

# Create your views here.
