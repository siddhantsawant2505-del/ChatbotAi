from django.urls import path
from backend import views


urlpatterns = [
    path('',views.home,name='home'),
    path('test-api/', views.chat_api, name='test_api'),
    path('chat-view/', views.chat_view, name='chat'),
    path('chat/', views.chat, name='chat')
]
