"""
URL configuration для marketplace приложения.
"""
from django.urls import path
from .views import (
    TaskListView, TaskCreateView, TaskDetailView, AcceptOfferView,
    MarkDealPaidView, MarkDealCompletedView, create_review,
    my_tasks, my_offers, my_deals,
    PortfolioListView, PortfolioCreateView, PortfolioUpdateView, PortfolioDeleteView,
    get_specialist_data, SpecialistDetailView,
    BookingListView, UpdateBookingStatusView,
    ConversationListView, ConversationDetailView, start_conversation,
    safe_deal_view, how_it_works_view, pricing_view, help_view,
    privacy_policy_view, terms_of_service_view
)
from .api.search import search_suggestions
from .api.booking import get_availability, create_booking

app_name = 'marketplace'

urlpatterns = [
    # Specialists
    path('specialists/<int:pk>/', SpecialistDetailView.as_view(), name='specialist_detail'),
    # Tasks
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
    # Портфолио
    path('my/portfolio/', PortfolioListView.as_view(), name='portfolio_list'),
    path('my/portfolio/add/', PortfolioCreateView.as_view(), name='portfolio_add'),
    path('my/portfolio/<int:pk>/edit/', PortfolioUpdateView.as_view(), name='portfolio_edit'),
    path('my/portfolio/<int:pk>/delete/', PortfolioDeleteView.as_view(), name='portfolio_delete'),
    path('my/portfolio/<int:pk>/delete/', PortfolioDeleteView.as_view(), name='portfolio_delete'),
    # Бронирования
    path('my/bookings/', BookingListView.as_view(), name='booking_list'),
    path('bookings/<int:pk>/update-status/', UpdateBookingStatusView.as_view(), name='update_booking_status'),
    # Сообщения
    path('my/messages/', ConversationListView.as_view(), name='conversation_list'),
    path('my/messages/<int:pk>/', ConversationDetailView.as_view(), name='conversation_detail'),
    path('start-conversation/<int:specialist_id>/', start_conversation, name='start_conversation'),
    # API
    path('api/specialist/<int:specialist_id>/', get_specialist_data, name='get_specialist_data'),
    path('api/search/suggestions/', search_suggestions, name='search_suggestions'),
    path('api/specialist/<int:specialist_id>/availability/', get_availability, name='get_availability'),
    path('api/bookings/create/', create_booking, name='create_booking'),
    # Статические страницы
    path('safe-deal/', safe_deal_view, name='safe_deal'),
    path('how-it-works/', how_it_works_view, name='how_it_works'),
    path('pricing/', pricing_view, name='pricing'),
    path('help/', help_view, name='help'),
    path('privacy-policy/', privacy_policy_view, name='privacy_policy'),
    path('terms-of-service/', terms_of_service_view, name='terms_of_service'),
]

