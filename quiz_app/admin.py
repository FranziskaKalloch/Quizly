from django.contrib import admin

from quiz_app.models import Quiz, Questions

admin.site.register([Quiz, Questions])