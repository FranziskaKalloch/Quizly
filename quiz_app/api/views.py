from .serializers import QuestionSerializer, QuizCreateSerializer, QuizSerializer
from auth_app.api.views import CookieJWTAuthentication

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


class CreateQuizView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]
    
    def post(self, request):
        ''' Validates the submitted YouTube URL for an authenticated user. '''
        serializer = QuizCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quiz_url = serializer.validated_data["url"]
        serializer.save()
        return Response(QuizSerializer, status=status.HTTP_201_CREATED)