"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from aichat import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('conversations/', views.ConversationListView.as_view(), name='conversations'),
    path('chat/<int:conversation_id>/', views.chat, name='chat_detail'),
    path('chat/<int:conversation_id>/send/', views.send_message, name='send_message'),
    path('chat/<int:conversation_id>/messages/', views.get_messages, name='get_messages'),
    path('new-chat/', views.new_chat, name='new_chat'),
    path('delete-conversation/<int:pk>/', views.ConversationDeleteView.as_view(), name='delete_conversation'),
    path('users/', views.user_list, name='user_list'),
    path('api/response/', views.handle_response, name='handle_response'),
]