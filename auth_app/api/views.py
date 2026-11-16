from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

from .serializers import RegisterSerializer


class RegisterView(APIView):
    '''  '''
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save() # ruft die create Methode auf
        return Response({"detail": "User created successfully!"}, status.HTTP_201_CREATED)