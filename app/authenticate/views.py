from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User, Company, Storage
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    CompanySerializer,
    StorageSerializer
)


class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'Пользователь успешно создан',
                'user_id': user.id,
                'email': user.email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response({
                'access': serializer.validated_data['access'],
                'refresh': serializer.validated_data['refresh'],
                'email': serializer.validated_data['user'].email
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompanyView(APIView):
    def get(self, request):
        if hasattr(request.user, 'company'):
            serializer = CompanySerializer(request.user.company)
            return Response(serializer.data)
        return Response({'detail': 'Компания не найдена'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        if hasattr(request.user, 'company'):
            return Response(
                {'detail': 'У пользователя уже есть компания'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            company = serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        if not hasattr(request.user, 'company'):
            return Response(
                {'detail': 'Компания не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CompanySerializer(
            request.user.company,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        if not hasattr(request.user, 'company'):
            return Response(
                {'detail': 'Компания не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        company = request.user.company
        company.delete()
        return Response({'detail': 'Компания удалена'}, status=status.HTTP_204_NO_CONTENT)


class StorageView(APIView):
    def get(self, request):
        if not hasattr(request.user, 'company'):
            return Response(
                {'detail': 'Компания не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        storages = Storage.objects.filter(company=request.user.company)
        serializer = StorageSerializer(storages, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not hasattr(request.user, 'company'):
            return Response(
                {'detail': 'Компания не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = StorageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(company=request.user.company)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StorageDetailView(APIView):
    def get_object(self, pk, user):
        try:
            storage = Storage.objects.get(pk=pk)
            if hasattr(user, 'company') and storage.company == user.company:
                return storage
            return None
        except Storage.DoesNotExist:
            return None

    def get(self, request, pk):
        storage = self.get_object(pk, request.user)
        if not storage:
            return Response(
                {'detail': 'Склад не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = StorageSerializer(storage)
        return Response(serializer.data)

    def put(self, request, pk):
        storage = self.get_object(pk, request.user)
        if not storage:
            return Response(
                {'detail': 'Склад не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = StorageSerializer(storage, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        storage = self.get_object(pk, request.user)
        if not storage:
            return Response(
                {'detail': 'Склад не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        storage.delete()
        return Response({'detail': 'Склад удален'}, status=status.HTTP_204_NO_CONTENT)


