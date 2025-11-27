from django.http import JsonResponse

def index(request):
    return JsonResponse({
        "message": "Welcome to ServiceMarket API",
        "version": "1.0",
        "endpoints": {
            "auth": "/api/v1/users/auth/",
            "services": "/api/v1/services/",
            "orders": "/api/v1/orders/",
            "chat": "/api/v1/chat/",
            "notifications": "/api/v1/notifications/"
        }
    })
