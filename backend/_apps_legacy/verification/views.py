from rest_framework import generics, permissions
from .models import VerificationDocument
from .serializers import VerificationDocumentSerializer

class DocumentListCreateView(generics.ListCreateAPIView):
    serializer_class = VerificationDocumentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return VerificationDocument.objects.filter(specialist=self.request.user)
