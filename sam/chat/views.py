import google.generativeai as genai
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Conversation, Message
import logging
from .models import Puzzle, PlayerProgress
from django.views.decorators.csrf import csrf_protect
import json
# Configure logging
logger = logging.getLogger(__name__)

# Configure the Gemini API
genai.configure(api_key="AIzaSyDOzfrBDzZIdMFojmjHebLXUkIvAiOo_l4")

def landing_page(request):
    if request.user.is_authenticated:
        return redirect('chat_home')
    return render(request, 'chat/landing.html')

def features_view(request):
    return render(request, "chat/features.html")

def games_view(request):
    return render(request, "chat/games.html")  



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('chat_home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'chat/login.html')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('chat_home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    
    return render(request, 'chat/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
@ensure_csrf_cookie
def chat_home(request):
    conversations = Conversation.objects.filter(user=request.user)
    return render(request, 'chat/home.html', {'conversations': conversations})

@login_required(login_url='login')
def get_ai_response(request):
    print(1)
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method', 'status': 'error'}, status=400)

    # Validate input
    user_input = request.POST.get('message')
    if not user_input:
        return JsonResponse({'error': 'Message is required', 'status': 'error'}, status=400)

    conversation_id = request.POST.get('conversation_id')
    
    try:
        # Get or create conversation
        if conversation_id:
            print(2)
            conversation = Conversation.objects.get(id=conversation_id, user=request.user)
        else:
            print(3)
            conversation = Conversation.objects.create(
                user=request.user,
                title=user_input[:50]  # Use first 50 chars as title
            )

        # Save user message
        Message.objects.create(
            conversation=conversation,
            content=user_input,
            is_bot=False
        )

        # Create a model instance with the correct model name
        model = genai.GenerativeModel("gemini-1.5-flash-latest")




        print(4)
        
        # Generate content with proper configuration
        response = model.generate_content(
            user_input,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            },
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        )

        # Get the response text
        ai_response = response.text

        # Save AI response
        Message.objects.create(
            conversation=conversation,
            content=ai_response,
            is_bot=True
        )

        return JsonResponse({
            'response': ai_response,
            'conversation_id': conversation.id,
            'status': 'success'
        })
        
    except Conversation.DoesNotExist:
        logger.error(f"Conversation not found: {conversation_id}")
        return JsonResponse({
            'error': 'Conversation not found',
            'status': 'error'
        }, status=404)
    except Exception as e:
        logger.error(f"Error in get_ai_response: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': str(e),
            'status': 'error'
        }, status=500)
        
def games(request):
    user_progress, created = PlayerProgress.objects.get_or_create(user=request.user)
    
    # Fetch the puzzle for the current level
    puzzle = Puzzle.objects.filter(level=user_progress.current_level).first()

    if request.method == "POST":
        selected_option = int(request.POST.get("selected_option"))

        if selected_option == puzzle.correct_option:
            user_progress.score += 10  # Increase score
            user_progress.advance_level()
            return redirect('games')  # Load the next level
        
        else:
            # Give a penalty if wrong
            user_progress.score -= 5
            user_progress.save()

    return render(request, "games.html", {"puzzle": puzzle, "level": user_progress.current_level, "score": user_progress.score})

def chatbot_response(user_message):
    if "games" in user_message.lower():
        return "🎮 Welcome to Aptitude Games! <a href='/games/'>Play Now</a>"
    return "I'm not sure about that, but I can help with finances!"

