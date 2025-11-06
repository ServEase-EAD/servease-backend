from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth.models import User
from .models import Employee
from .serializers import EmployeeProfileSerializer, ChangePasswordSerializer, AssignedTaskSerializer
from .permissions import IsEmployeeOwnerOrAdmin
import requests
from django.conf import settings

class ProfileView(generics.RetrieveAPIView):
    serializer_class = EmployeeProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Debug logging
        print(f"DEBUG: User authenticated: {self.request.user}")
        print(f"DEBUG: User is_authenticated: {self.request.user.is_authenticated}")
        print(f"DEBUG: User email: {self.request.user.email}")
        
        # Get or create employee profile for the authenticated user
        employee, created = Employee.objects.get_or_create(
            user=self.request.user,
            defaults={
                'status': 'Active',
                'access_role': 'Employee',
            }
        )
        
        if created:
            print(f"DEBUG: New employee profile created for {self.request.user}")
        
        return employee


class UpdateProfileView(generics.UpdateAPIView):
    serializer_class = EmployeeProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Get or create employee profile for the authenticated user
        employee, created = Employee.objects.get_or_create(
            user=self.request.user,
            defaults={
                'status': 'Active',
                'access_role': 'Employee',
            }
        )
        return employee


class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)


class EmployeeListCreateView(generics.ListCreateAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Employee.objects.all()
        specialization = self.request.query_params.get("specialization", None)
        is_available = self.request.query_params.get("is_available", None)

        if specialization:
            queryset = queryset.filter(specialization=specialization)
        if is_available is not None:
            queryset = queryset.filter(is_available=is_available.lower() == "true")

        return queryset


class EmployeeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeProfileSerializer
    permission_classes = [IsAuthenticated, IsEmployeeOwnerOrAdmin]


class AssignedTasksPagination(PageNumberPagination):
    page_size = 10


class AssignedTasksViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = AssignedTasksPagination

    def list(self, request):
        try:
            employee_id = request.user.id
            appointment_service_url = f"{settings.SERVICE_URLS['APPOINTMENT_SERVICE']}/api/v1/appointments/employee/{employee_id}/"
            response = requests.get(
                appointment_service_url,
                headers={"Authorization": request.headers.get("Authorization")}
            )
            response.raise_for_status()
            appointments = response.json()

            for appointment in appointments.get("results", []):
                customer_service_url = f"{settings.SERVICE_URLS['CUSTOMER_SERVICE']}/api/v1/customers/{appointment['customer_id']}/"
                try:
                    customer_response = requests.get(
                        customer_service_url,
                        headers={"Authorization": request.headers.get("Authorization")}
                    )
                    if customer_response.status_code == 200:
                        customer = customer_response.json()
                        appointment["customer_name"] = f"{customer.get('first_name', 'Unknown')} {customer.get('last_name', '')}"
                    else:
                        appointment["customer_name"] = "Unknown"
                except:
                    appointment["customer_name"] = "Unknown"

                vehicle_service_url = f"{settings.SERVICE_URLS['VEHICLE_SERVICE']}/api/v1/vehicles/{appointment['vehicle_id']}/"
                try:
                    vehicle_response = requests.get(
                        vehicle_service_url,
                        headers={"Authorization": request.headers.get("Authorization")}
                    )
                    if vehicle_response.status_code == 200:
                        vehicle = vehicle_response.json()
                        appointment["vehicle_details"] = f"{vehicle.get('make', 'Unknown')} {vehicle.get('model', 'Vehicle')}"
                    else:
                        appointment["vehicle_details"] = "Unknown Vehicle"
                except:
                    appointment["vehicle_details"] = "Unknown Vehicle"

            paginator = self.pagination_class()
            page = paginator.paginate_queryset(appointments.get("results", []), request)
            serializer = AssignedTaskSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        except requests.RequestException as e:
            return Response(
                {"error": "Error fetching assigned tasks", "detail": str(e)},
                status=500
            )
