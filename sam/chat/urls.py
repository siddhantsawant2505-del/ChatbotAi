# urls.py
from django.urls import path
from . import views
from .views import features_view
from .views import games_view

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('features/', features_view, name='features'),
    path("games/", games_view, name="games"),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('chat/', views.chat_home, name='chat_home'),
    path('get-response/', views.get_ai_response, name='get_ai_response'),
    
]
