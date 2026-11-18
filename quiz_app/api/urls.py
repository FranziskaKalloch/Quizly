from django.urls import path
from .views import CreateQuizView, RetrieveUpdateDestroyQuizView

urlpatterns = [
    path('quizzes/', CreateQuizView.as_view(), name="create_quiz"),
    path('quizzes/<int:id>/', RetrieveUpdateDestroyQuizView.as_view(), name="quiz")
]
