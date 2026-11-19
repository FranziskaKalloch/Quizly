from rest_framework import serializers

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class RegisterSerializer(serializers.Serializer):
    """Handle user registration, including password validation."""

    password = serializers.CharField(write_only=True)
    confirmed_password = serializers.CharField(write_only=True)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
        
    def validate(self, data):
        """Validate passwords and check account availability."""
        email = data.get('email')
        username = data.get('username')
        
        if data['password'] != data["confirmed_password"]:
            raise serializers.ValidationError({
                "password": "Die Passwörter stimmen nicht überein!"
            })
        
        try: 
            validate_password(password=data['password'])
        except ValidationError as error: 
            raise serializers.ValidationError({"password": error.messages}) from error
            
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError({
                "email": "Die E-Mail Adresse ist bereits vergeben"
            })
        
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({
                "username": "Dieser Benutzername ist bereits vergeben."
            })
        
        return data
            
    def create(self, validated_data):
        """Create and return a new user with a hashed password."""
        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']
        
        new_user = User.objects.create_user(
            username = username,
            password = password,
            email = email,
        )
        return new_user

class LoginSerializer(serializers.Serializer):
    """Validate the username and password fields in a login request."""

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    
    