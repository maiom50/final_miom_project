from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Supplier
from .serializers import SupplierSerializer
from authenticate.permissions import IsCompanyMember, IsCompanyOwner
from authenticate.models import User, Employee
from authenticate.serializers import CompanyEmployeeSerializer


class SupplierView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCompanyMember]

    def get(self, request):
        if not hasattr(request.user, 'owned_company'):
            return Response(
                {'detail': 'Компания не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        suppliers = Supplier.objects.filter(company=request.user.owned_company)
        serializer = SupplierSerializer(suppliers, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not hasattr(request.user, 'owned_company'):
            return Response(
                {'detail': 'Компания не найдена'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SupplierSerializer(data=request.data)
        if serializer.is_valid():
            supplier = serializer.save(company=request.user.owned_company)
            return Response(SupplierSerializer(supplier).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SupplierDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCompanyMember]

    def get_object(self, pk, user):
        try:
            supplier = Supplier.objects.get(pk=pk)
            if hasattr(user, 'owned_company') and supplier.company == user.owned_company:
                return supplier
            return None
        except Supplier.DoesNotExist:
            return None

    def get(self, request, pk):
        supplier = self.get_object(pk, request.user)
        if not supplier:
            return Response(
                {'detail': 'Поставщик не найден'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = SupplierSerializer(supplier)
        return Response(serializer.data)

    def put(self, request, pk):
        supplier = self.get_object(pk, request.user)
        if not supplier:
            return Response(
                {'detail': 'Поставщик не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = SupplierSerializer(supplier, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        supplier = self.get_object(pk, request.user)
        if not supplier:
            return Response(
                {'detail': 'Поставщик не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

        supplier.delete()
        return Response({'detail': 'Поставщик удален'}, status=status.HTTP_204_NO_CONTENT)


class CompanyEmployeeView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsCompanyOwner]

    def get(self, request):
        """Получить список сотрудников компании"""
        if not hasattr(request.user, 'owned_company'):
            return Response(
                {'detail': 'У вас нет компании'},
                status=status.HTTP_404_NOT_FOUND
            )

        employees = request.user.owned_company.employees_list
        return Response({
            'employees': [
                {
                    'id': getattr(emp, 'id', None),
                    'email': emp.user.email,
                    'position': getattr(emp, 'position', 'Владелец'),
                    'is_active': getattr(emp, 'is_active', True),
                    'is_owner': emp.user == request.user
                }
                for emp in employees
            ]
        })

    def post(self, request):
        """Прикрепить пользователя к компании"""
        if not hasattr(request.user, 'owned_company'):
            return Response(
                {'detail': 'У вас нет компании'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CompanyEmployeeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        email = data['email']
        position = data.get('position', '')

        try:
            user = User.objects.get(email=email)

            if hasattr(user, 'owned_company') and user.owned_company == request.user.owned_company:
                return Response(
                    {'detail': 'Пользователь уже является владельцем этой компании'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if hasattr(user, 'employee_profile'):
                if user.employee_profile.company == request.user.owned_company:
                    return Response(
                        {'detail': 'Пользователь уже прикреплен к вашей компании'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    return Response(
                        {'detail': 'Пользователь уже прикреплен к другой компании'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            Employee.objects.create(
                user=user,
                company=request.user.owned_company,
                position=position
            )

            return Response(
                {'detail': 'Пользователь успешно прикреплен к компании'},
                status=status.HTTP_201_CREATED
            )

        except User.DoesNotExist:
            return Response(
                {'detail': 'Пользователь не найден'},
                status=status.HTTP_404_NOT_FOUND
            )

    def delete(self, request, user_id=None):
        """Удалить сотрудника из компании"""
        if not hasattr(request.user, 'owned_company'):
            return Response(
                {'detail': 'У вас нет компании'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            employee = Employee.objects.get(
                id=user_id,
                company=request.user.owned_company
            )

            if employee.user == request.user:
                return Response(
                    {'detail': 'Нельзя удалить себя из компании'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            employee.delete()
            return Response(
                {'detail': 'Сотрудник удален из компании'},
                status=status.HTTP_204_NO_CONTENT
            )

        except Employee.DoesNotExist:
            return Response(
                {'detail': 'Сотрудник не найден'},
                status=status.HTTP_404_NOT_FOUND
            )