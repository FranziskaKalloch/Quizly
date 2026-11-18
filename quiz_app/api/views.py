import logging

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auth_app.api.views import CookieJWTAuthentication

from .functions import QuizCreationError, create_quiz_from_url
from .serializers import QuizCreateSerializer, QuizSerializer
from ..models import Quiz


logger = logging.getLogger(__name__)


class CreateQuizView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def post(self, request):
        """Create a quiz from the submitted YouTube URL and return it with its questions."""
        serializer = QuizCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            quiz = create_quiz_from_url(serializer.validated_data["url"], request.user)
        except QuizCreationError as error:
            logger.exception("Quiz creation failed.")
            raise APIException("Das Quiz konnte nicht erstellt werden.") from error

        return Response(QuizSerializer(quiz).data, status=status.HTTP_201_CREATED)

    def get(self, request):
        """Return the authenticated user's quizzes and their questions."""
        quizzes = Quiz.objects.filter(owner=request.user).prefetch_related("quiz_question")
        serializer = QuizSerializer(quizzes, many=True, context={"include_question_timestamps": False})
        return Response(serializer.data, status=status.HTTP_200_OK)
