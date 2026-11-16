from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate

from .serializers import RegisterSerializer, LoginSerializer


class RegisterView(APIView):
    '''Validate the registration data, create a new user, and return a 201 Created response.'''
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) # sorgt dafür das ungültige Daten als 400 zurückkommen
        serializer.save() # ruft die create Methode auf
        return Response({"detail": "User created successfully!"}, status.HTTP_201_CREATED)
    

class LoginView(APIView):
    '''Authenticate the user and return their account details on success or a 401 response if the credentials are invalid.'''
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username'] # das sind die WErte, die der SErializer geprüft hat
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response(
                {"detail": "Ungültige Anmeldedaten."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            
        def get_tokens_for_user(user):
            if not user.is_active: # ist das Benutzerkonto aktiv?
                raise AuthenticationFailed("User ist nicht aktiv")   
            
            refresh = RefreshToken.for_user(user) # generiert einen Refresh Token
            return {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                    }
        tokens = get_tokens_for_user(user)
        
        response = Response({
            "detail": "Login successfully!",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }, status=status.HTTP_200_OK)
        
        response.set_cookie("access_token", tokens["access"], httponly=True)
        response.set_cookie("refresh_token", tokens["refresh"], httponly=True)
        return response 