import logging

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView

from auth_app.api.views import CookieJWTAuthentication

from .functions import QuizCreationError, create_quiz_from_url
from .serializers import QuizCreateSerializer, QuizSerializer
from ..models import Quiz
from .permissions import IsQuizOwner

logger = logging.getLogger(__name__)

class CreateQuizView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request):
        """Generate and return a quiz from a YouTube URL."""
        serializer = QuizCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            quiz = create_quiz_from_url(serializer.validated_data["url"], request.user)
        except QuizCreationError as error:
            logger.exception("Quiz creation failed.")
            raise APIException("Das Quiz konnte nicht erstellt werden.") from error

        return Response(QuizSerializer(quiz).data, status=status.HTTP_201_CREATED)
    
    def get(self, request):
        """Return all quizzes for the authenticated user."""
        quizzes = Quiz.objects.filter(owner=request.user).prefetch_related("quiz_question")
        serializer = QuizSerializer(quizzes, many=True, context={"include_question_timestamps": False},)
        return Response(serializer.data, status=status.HTTP_200_OK)    

class RetrieveUpdateDestroyQuizView(RetrieveUpdateDestroyAPIView):
    """Allow owners to retrieve, update, or delete their quizzes."""

    permission_classes = [IsAuthenticated, IsQuizOwner]
    authentication_classes = [CookieJWTAuthentication]
    serializer_class = QuizSerializer 
    lookup_url_kwarg = "id"
    
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']
    
    def get_queryset(self):
        """Return the queryset used to look up a quiz by its ID."""
        return Quiz.objects.all()
    
    def get_serializer_context(self):
        """Exclude question timestamps from serializer output."""
        context = super().get_serializer_context()
        context["include_question_timestamps"] = False
        return context

