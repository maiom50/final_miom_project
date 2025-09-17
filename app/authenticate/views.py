from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from .models import User, Company, Storage
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    CompanySerializer,
    StorageSerializer,
    CompanyCreateSerializer
)

class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={201: UserRegistrationSerializer},
        examples=[
            OpenApiExample(
                'Example',
                value={
                    'email': 'user@example.com',
                    'password': 'securepassword123'
                }
            )
        ]
    )
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

    @extend_schema(
        request=UserLoginSerializer,
        responses={200: UserLoginSerializer},
        examples=[
            OpenApiExample(
                'Example',
                value={
                    'email': 'user@example.com',
                    'password': 'securepassword123'
                }
            )
        ]
    )
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
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: CompanySerializer})
    def get(self, request):
        if hasattr(request.user, 'owned_company'):
            serializer = CompanySerializer(request.user.owned_company)
            return Response(serializer.data)
        return Response({'detail': 'Компания не найдена'}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        request=CompanyCreateSerializer,
        responses={201: CompanySerializer},
        examples=[
            OpenApiExample(
                'Example',
                value={
                    'name': 'Моя компания',
                    'inn': '1234567890',
                    'description': 'Описание компании'
                }
            )
        ]
    )
    def post(self, request):
        if hasattr(request.user, 'owned_company'):
            return Response(
                {'detail': 'У пользователя уже есть компания'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CompanyCreateSerializer(data=request.data)
        if serializer.is_valid():
            company = serializer.save(owner=request.user)
            return Response(CompanySerializer(company).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=CompanyCreateSerializer,
        responses={200: CompanySerializer}
    )
    def put(self, request):
        if not hasattr(request.user, 'owned_company'):
            return Response(
                {'detail': 'Компания не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CompanySerializer(
            request.user.owned_company,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        if not hasattr(request.user, 'owned_company'):
            return Response(
                {'detail': 'Компания не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        company = request.user.owned_company
        company.delete()
        return Response({'detail': 'Компания удалена'}, status=status.HTTP_204_NO_CONTENT)

class StorageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses={200: StorageSerializer(many=True)})
    def get(self, request):
        if not hasattr(request.user, 'owned_company'):
            return Response(
                {'detail': 'Компания не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        storages = Storage.objects.filter(company=request.user.owned_company)
        serializer = StorageSerializer(storages, many=True)
        return Response(serializer.data)

    @extend_schema(
        request=StorageSerializer,
        responses={201: StorageSerializer},
        examples=[
            OpenApiExample(
                'Example',
                value={
                    'name': 'Основной склад',
                    'address': 'г. Колпино, ул. Примерная, д. 1',
                    'capacity': 1000
                }
            )
        ]
    )
    def post(self, request):
        if not hasattr(request.user, 'owned_company'):
            return Response(
                {'detail': 'Компания не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = StorageSerializer(data=request.data)
        if serializer.is_valid():
            # Убираем поле company из запроса, оно проставляется автоматически
            storage_data = serializer.validated_data.copy()
            storage = Storage.objects.create(
                company=request.user.owned_company,
                **storage_data
            )
            return Response(StorageSerializer(storage).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StorageDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk, user):
        try:
            storage = Storage.objects.get(pk=pk)
            if hasattr(user, 'owned_company') and storage.company == user.owned_company:
                return storage
            return None
        except Storage.DoesNotExist:
            return None

    @extend_schema(responses={200: StorageSerializer})
    def get(self, request, pk):
        storage = self.get_object(pk, request.user)
        if not storage:
            return Response(
                {'detail': 'Склад не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = StorageSerializer(storage)
        return Response(serializer.data)

    @extend_schema(
        request=StorageSerializer,
        responses={200: StorageSerializer}
    )
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


