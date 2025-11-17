"""
URL configuration для marketplace приложения.
"""
from django.urls import path
from .views import (
    TaskListView, TaskCreateView, TaskDetailView, AcceptOfferView,
    MarkDealPaidView, MarkDealCompletedView, create_review,
    my_tasks, my_offers, my_deals
)

app_name = 'marketplace'

urlpatterns = [
    path('tasks/', TaskListView.as_view(), name='tasks_list'),
    path('tasks/create/', TaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', TaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:task_id>/review/<int:specialist_id>/', create_review, name='create_review'),
    path('offers/<int:offer_id>/accept/', AcceptOfferView.as_view(), name='accept_offer'),
    path('deals/<int:deal_id>/mark-paid/', MarkDealPaidView.as_view(), name='mark_deal_paid'),
    path('deals/<int:deal_id>/mark-completed/', MarkDealCompletedView.as_view(), name='mark_deal_completed'),
    # Личный кабинет
    path('my/tasks/', my_tasks, name='my_tasks'),
    path('my/offers/', my_offers, name='my_offers'),
    path('my/deals/', my_deals, name='my_deals'),
]

