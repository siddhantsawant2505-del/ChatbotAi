from django.shortcuts import render
from django.http import JsonResponse
import requests
import os

def home(request):
    return render(request, 'landing.html')

def chat_api(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)

        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return JsonResponse({'error': 'API key is missing'}, status=500)

        # API call to Gemini Flash 2.0
        url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.0-flash:generateContent?key=' + api_key
        headers = {'Content-Type': 'application/json'}
        data = {
            'contents': [{'parts': [{'text': user_message}]}]
        }

        try:
            response = requests.post(url, headers=headers, json=data)
            response_data = response.json()
            ai_response = response_data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'No response')
            return JsonResponse({'response': ai_response})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

import os
import json
from django.http import JsonResponse
from .models import Chat
from google.generativeai import GenerativeModel

def chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message')

            # Ensure API is configured
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                return JsonResponse({'error': 'API key not found'}, status=500)

            # Initialize Gemini Model
            model = GenerativeModel('gemini-1.5-flash', api_key=api_key)
            
            # Generate AI Response
            response = model.generate_content(user_message)
            ai_message = response.text

            # Save to Database
            Chat.objects.create(user_input=user_message, ai_response=ai_message)

            return JsonResponse({'response': ai_message})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests

@csrf_exempt
def chat_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')

            # Integrate Gemini Flash 2.0 API
            response = requests.post('https://api.gemini.com/v1/chat/completions', json={
                'messages': [{'role': 'user', 'content': user_message}],
                'model': 'gemini-flash-2.0'
            })

            ai_response = response.json().get('choices')[0]['message']['content']
            return JsonResponse({'response': ai_response})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request'}, status=400)

