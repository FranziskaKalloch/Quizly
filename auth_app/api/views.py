from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError, AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth import authenticate

from .serializers import RegisterSerializer, LoginSerializer


class RegisterView(APIView):
    """Handle registration requests and create new users."""

    permission_classes = [AllowAny]
    
    def post(self, request):
        """Validate registration data and create a user."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True) 
        serializer.save() 
        return Response({"detail": "User created successfully!"}, status.HTTP_201_CREATED)
    

class LoginView(APIView):
    """Authenticate users and return their account details."""

    permission_classes = [AllowAny]
    
    def post(self, request):
        """Authenticate the user and set an access-token cookie."""
        serializer = LoginSerializer(data=request.data) 
        serializer.is_valid(raise_exception=True) 
        username = serializer.validated_data['username'] 
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password) 
        
        if user is None: 
            return Response( 
                {"detail": "Ungültige Anmeldedaten."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            
        def get_tokens_for_user(user):
            """Return tokens for an active user."""
            if not user.is_active: 
                raise AuthenticationFailed("User ist nicht aktiv")   
            
            refresh = RefreshToken.for_user(user) 
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
        
        response.set_cookie("access_token", tokens["access"], httponly=True,secure=True) 
        return response 

class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate requests using an access-token cookie."""

    def authenticate(self, request):
        access_token = request.COOKIES.get("access_token")
        if access_token is None:
            return None
            
        validated_token = self.get_validated_token(access_token)
        user = self.get_user(validated_token)
        return (user, validated_token)
    
        
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]
    
    def post(self, request):
        """Revoke the refresh token and clear authentication cookies."""
        response = Response(
            {"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid"}, status=status.HTTP_200_OK
        )
    
        refresh_token = request.COOKIES.get("refresh_token")
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist() 
            except TokenError:
                pass 
        
        response.delete_cookie("access_token") 
        response.delete_cookie("refresh_token")
        return response
    
class RefreshTokenView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        """Validate the refresh cookie and renew the access token."""
        response = Response({
            "detail": "Token refreshed"
        }, status=status.HTTP_200_OK)
        
        refresh_token = request.COOKIES.get("refresh_token") 
        
        if refresh_token is None:
            return Response({
                "detail": "Refresh Token wurde nicht gefunden!"
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            token = RefreshToken(refresh_token)
        except TokenError: 
            return Response({
                "detail": "Refresh Token ist nicht valide"
            }, status=status.HTTP_401_UNAUTHORIZED)
            
        access_token = str(token.access_token)
        
        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="Lax")
        return response
        