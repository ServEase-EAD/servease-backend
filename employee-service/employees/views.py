from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User
from .models import Employee
from .serializers import EmployeeProfileSerializer, ChangePasswordSerializer, AssignedTaskSerializer, AdminEmployeeCreateUpdateSerializer
from .permissions import IsEmployeeOwnerOrAdmin
import requests
from django.conf import settings

class ProfileView(generics.RetrieveUpdateAPIView):
    """
    Handle both GET and PUT requests for employee profile.
    GET: Retrieve employee profile
    PUT/PATCH: Update employee profile
    """
    serializer_class = EmployeeProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Get employee profile for the authenticated user.
        The CustomJWTAuthentication automatically creates Employee profile
        if it doesn't exist, so we should always find one.
        """
        try:
            # Get employee profile for the authenticated user
            employee = Employee.objects.get(user=self.request.user)
            print(f"DEBUG: Found employee profile for {self.request.user.email}")
            return employee
        except Employee.DoesNotExist:
            # This should not happen due to CustomJWTAuthentication, but handle it just in case
            print(f"DEBUG: Employee profile not found for {self.request.user.email}, creating...")
            employee = Employee.objects.create(user=self.request.user)
            return employee

    def update(self, request, *args, **kwargs):
        """
        Override update to add logging and ensure proper response
        """
        partial = kwargs.pop('partial', True)  # Allow partial updates by default
        instance = self.get_object()
        
        print(f"DEBUG: Updating employee profile for user {request.user.email}")
        print(f"DEBUG: Update data: {request.data}")
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        # Perform the update
        updated_instance = serializer.save()
        
        print(f"DEBUG: Successfully updated employee profile: {updated_instance.id}")
        
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password updated successfully"}, status=status.HTTP_200_OK)


class EmployeeListCreateView(generics.ListCreateAPIView):
    queryset = Employee.objects.select_related('user').all()
    serializer_class = EmployeeProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Employee.objects.select_related('user').all()
        specialization = self.request.query_params.get("specialization", None)
        is_available = self.request.query_params.get("is_available", None)

        if specialization:
            queryset = queryset.filter(specialization=specialization)
        if is_available is not None:
            queryset = queryset.filter(is_available=is_available.lower() == "true")

        return queryset


class EmployeeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.select_related('user').all()
    serializer_class = EmployeeProfileSerializer
    permission_classes = [IsAuthenticated, IsEmployeeOwnerOrAdmin]


class EmployeeBasicInfoView(generics.RetrieveAPIView):
    """
    Retrieve basic employee information (name, email) for service-to-service communication.
    This endpoint is less restrictive to allow other services to get employee names
    for display purposes (e.g., appointment listings).
    """
    queryset = Employee.objects.select_related('user').all()
    serializer_class = EmployeeProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['basic_info_only'] = True
        return context


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


@api_view(['POST', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def admin_create_or_update_employee_profile(request, employee_id):
    """
    Admin endpoint to create or update employee profile with full details.
    This should be called after creating an employee account in the authentication service.
    
    POST/PUT/PATCH /api/v1/employees/admin/<employee_id>/profile/
    
    Body: {
        "phone_number": "1234567890",
        "gender": "Male",
        "date_of_birth": "1990-01-01",
        "address_line1": "123 Main St",
        "address_line2": "Apt 4B",
        "city": "New York",
        "postal_code": "10001",
        "specialization": "Engine Repair",
        "experience_years": 5,
        "hourly_rate": 50.00,
        "is_available": true
    }
    """
    # Check if user is admin (has role 'admin')
    if not hasattr(request.user, 'role') or request.user.role != 'admin':
        return Response(
            {"error": "Only admin users can create or update employee profiles"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        # Try to get existing employee profile
        employee = Employee.objects.get(id=employee_id)
        print(f"DEBUG Admin: Updating existing employee profile {employee_id}")
        
        serializer = AdminEmployeeCreateUpdateSerializer(employee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            print(f"DEBUG Admin: Successfully updated employee {employee_id}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            print(f"DEBUG Admin: Validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
    except Employee.DoesNotExist:
        print(f"DEBUG Admin: Employee profile {employee_id} does not exist, creating new one")
        
        # Create new employee profile
        # Need to get or create the User object first
        try:
            # The employee_id from authentication service should be used as the Employee id
            # We need to fetch user details from the authentication service or create a stub user
            # For now, we'll create a basic user record if it doesn't exist
            
            # Check if a User with this employee's email exists
            # Since we don't have email here, we'll create Employee without User first
            # The User will be created when employee first logs in via CustomJWTAuthentication
            
            employee = Employee.objects.create(id=employee_id)
            print(f"DEBUG Admin: Created new employee profile {employee_id}")
            
            serializer = AdminEmployeeCreateUpdateSerializer(employee, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                print(f"DEBUG Admin: Successfully populated new employee {employee_id}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                # If validation fails, delete the created employee
                employee.delete()
                print(f"DEBUG Admin: Validation errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            print(f"DEBUG Admin: Error creating employee: {str(e)}")
            return Response(
                {"error": f"Failed to create employee profile: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
