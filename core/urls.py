from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include("auth_app.api.urls")),
    #path('api', include("quiz_app.api.urls")),
    
    path('api/token/', TokenObtainPairView.as_view()),
]
