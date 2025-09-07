from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

class SalesView(APIView):
    def get(self, request):
        return Response({'message': 'Sales endpoint'}, status=status.HTTP_200_OK)