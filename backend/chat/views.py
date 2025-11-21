from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.db.models import Q
from .models import Conversation, Message
from backend.marketplace.models import Deal

class ConversationDetailView(LoginRequiredMixin, DetailView):
    """
    Страница диалога.
    """
    model = Conversation
    template_name = 'chat/conversation.html'
    context_object_name = 'conversation'
    
    def get_queryset(self):
        # Пользователь видит только свои диалоги
        return Conversation.objects.filter(participants=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Помечаем сообщения как прочитанные
        self.object.messages.exclude(sender=self.request.user).update(is_read=True)
        return context
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        text = request.POST.get('text', '').strip()
        
        if text:
            Message.objects.create(
                conversation=self.object,
                sender=request.user,
                text=text
            )
            
        return redirect('chat:detail', pk=self.object.pk)

@login_required
def start_conversation(request, deal_id):
    """
    Начать диалог по сделке.
    """
    deal = get_object_or_404(Deal, id=deal_id)
    
    # Проверяем, что пользователь участник сделки
    if request.user not in [deal.client, deal.specialist]:
        return HttpResponseForbidden("Вы не участник этой сделки")
        
    # Проверяем, есть ли уже диалог
    conversation = Conversation.objects.filter(deal=deal).first()
    
    if not conversation:
        conversation = Conversation.objects.create(deal=deal)
        conversation.participants.add(deal.client, deal.specialist)
        
    return redirect('chat:detail', pk=conversation.pk)
