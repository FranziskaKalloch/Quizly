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
        ''' Validate the login request, authenticate the user, and return their account details with access and refresh tokens set as HTTP-only cookies. '''
        serializer = LoginSerializer(data=request.data) # übergibt den von DRF aufbereiteten Inhalt der Anfrage an den Serializer, hier Benutzername und Passwort
        serializer.is_valid(raise_exception=True) # prüft die Eingabe des Users. Fehlt z.B. das Passwort, antwortet DRF standardmäßig mit 400 Bad Request
        username = serializer.validated_data['username'] # liest die geprüften WErte (username) aus dem Serializer
        password = serializer.validated_data['password']
        # Zugangsdaten prüfen und Tokens erzeugen
        user = authenticate(username=username, password=password) # prüft die Zugangsdaten. Sind beide Felder gültig, aber das Passwort ist falsch, gibt authenticat hier None zurück und die View antworte mit 401 Unauthorized
        
        if user is None: # prüft, ob Django den Anmeldeversuch abgelehnt hat. Das passiert z.B. bei einem falschen Passwort.
            return Response( # Beendet die Methode sofort und schickt 401 Unauthorized mit der Meldung
                {"detail": "Ungültige Anmeldedaten."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
            
        def get_tokens_for_user(user):
            ''' Return access and refresh tokens for an active user. Raise AuthenticationFailed if the account is inactive. '''
            if not user.is_active: # ist das Benutzerkonto aktiv? also prüft, ob das Konto deaktiviert ist.
                raise AuthenticationFailed("User ist nicht aktiv")   
            
            refresh = RefreshToken.for_user(user) # generiert mit Simple JWT einen Refresh-Token für dieses Konto
            return { # Gibt ein Dictionary mit beiden Tokens zurück. refresh.access_token erzeugt den zugehörigen Access-Token. str(...) wandelt die Token-Objekte in Zeichenketten um, damit du sie als Cookie-Werte verwenden kannst.
                    "refresh": str(refresh),
                    "access": str(refresh.access_token)
                    }
        tokens = get_tokens_for_user(user)
        
        response = Response({ # Baut die Erfolgsantwort mit 200 OK. detail enthält die Meldung.
            "detail": "Login successfully!",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email
            }
        }, status=status.HTTP_200_OK)
        
        response.set_cookie("access_token", tokens["access"], httponly=True,secure=True) # Fügt der Antwort einen Set-Cookie-Header mit dem Access-Token hinzu. Der Browser kann ihn speichern und bei passenden Folgeanfragen mitsenden.
        response.set_cookie("refresh_token", tokens["refresh"], httponly=True, secure=True) # Fügt einen zweiten Set-Cookie-Header mit dem Refresh-Token hinzu.
        return response 
# COOKIE
# Ein Cookie ist ein benannter Wert, den der Browser speichert und bei passenden Anfragen wieder an den Server schickt. In Quizly ist der Token der Wert und der Cookie der Weg, auf dem der Wert zwischen Browser und Backend übertragen wird

class CookieJWTAuthentication(JWTAuthentication):
    ''' Authenticate requests using the access token stored in a cookie. '''
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
        ''' Log out the authenticated user by revoking the refresh token if it is present and valid, and clearing both authentication cookies. '''
        response = Response(
            {"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid"}, status=status.HTTP_200_OK
        )
        # Refresh Token aus dem Cookie lesen und blacklisten
        refresh_token = request.COOKIES.get("refresh_token") # liest den Wert, den der Browser mit der Logout-Anfrage geschickt hat. Diesen Wert braucht man, um den Refresh-Token serverseitig zu sperren.
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist() # Blacklisten bedeutet hier serverseitig sperren. 
            except TokenError:
                pass # Token bereits ungültig oder abgelaufen
        
        # Cookies im Browser löschen
        response.delete_cookie("access_token") # fügt der Antwort einen Set-Cookie-Header hinzu, der den Cookie sofort ablaufen lässt. Dafür genügt der Cookie-Name.
        response.delete_cookie("refresh_token")
        return response
        
        
        
        
        