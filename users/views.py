from rest_framework.views import APIView
from .serializers import UserSerializers
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from .models import User
import jwt, datetime


class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def get(self, request):
        all_users = User.objects.all()
        serializer = UserSerializers(all_users, many=True)
        data = {
            "Message": "Ro'yxatdan o'tganlar",
            "data": serializer.data
        }
        return Response(data)


class LoginView(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['user_password']

        user = User.objects.filter(username=username).first()

        if user is None:
            raise AuthenticationFailed("User Not Found!")

        if not user.check_password(password):
            raise AuthenticationFailed("Incorrect Password")

        payload = {
            "id": user.id,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            "iat": datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'secret', algorithm="HS256")

        response = Response()
        response.set_cookie(
            key='jwt',
            value=token,
            httponly=True
        )

        response.data = ({
            "jwt": token
        })
        return response


class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')
        if not token:
            raise AuthenticationFailed("Authentication credentials were not provided.")
        try:
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token is expired.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token.')

        user_id = payload['id']
        user = User.objects.filter(id=user_id).first()
        if not user:
            raise AuthenticationFailed('User not found.')

        serializer = UserSerializers(user)
        return Response(serializer.data)


class LogOutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            "message": 'success'
        }
        return response


