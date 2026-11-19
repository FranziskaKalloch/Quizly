from django.contrib import admin

from quiz_app.models import Quiz, Question

admin.site.register([Quiz, Question])