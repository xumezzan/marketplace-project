from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('conversation/<int:pk>/', views.ConversationDetailView.as_view(), name='detail'),
    path('start/<int:deal_id>/', views.start_conversation, name='start'),
]
