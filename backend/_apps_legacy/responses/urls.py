from django.urls import path
from .views import RequestResponseView, MyResponsesView, MarkResponseViewedView

urlpatterns = [
    # Specialist actions
    path('request/<int:pk>/', RequestResponseView.as_view(), name='respond-to-request'),
    path('my/', MyResponsesView.as_view(), name='my-responses'),
    # Client actions
    path('<int:pk>/view/', MarkResponseViewedView.as_view(), name='mark-response-viewed'),
]
