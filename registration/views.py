
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from .serializers import  RegistrationSerializer
from django.http import Http404
import datetime
import jwt
from django.conf import settings
from .models import Registration
 
# Register view
class RegisterView(APIView):
    permission_classes = [AllowAny]  # Allow access without authentication
 
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
 
 
# Login view
class LoginView(APIView):
    permission_classes = [AllowAny]  # Allow access without authentication
 
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
 
        user = Registration.objects.filter(email=email).first()
 
        if user is None:
            raise AuthenticationFailed('User not found!')
 
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect password!')
 
        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }
 
        secret_key = settings.SECRET_KEY
        token = jwt.encode(payload, secret_key, algorithm='HS256')
 
        response = Response()
        response.set_cookie(key='jwt', value=token, httponly=True)
        response.data = {
            'jwt': token
        }
        return response
 
 
# User view to test authentication
class UserView(APIView):
    # permission_classes = [IsAuthenticated]
 
    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise AuthenticationFailed('Unauthenticated!')
 
        token = auth_header.split(' ')[1]
        secret_key = settings.SECRET_KEY
 
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
 
        user = Registration.objects.filter(id=payload['id']).first()
 
        if user is None:
            raise AuthenticationFailed('User not found!')
 
        serializer = RegistrationSerializer(user)
        return Response(serializer.data)
 
 
 
class LogoutView(APIView):
    # permission_classes = [IsAuthenticated]
 
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response