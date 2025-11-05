from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from django.contrib.auth.models import User
from employees.models import Employee


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication that handles cross-service authentication.
    
    The authentication service uses CustomUser with UUID primary keys,
    but this service uses Django's default User model with integer IDs.
    
    This class extracts user information from the JWT token and either
    finds or creates a matching User in this service's database.
    """
    
    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        Creates a user if it doesn't exist.
        """
        try:
            # Extract user information from token claims
            user_id_from_token = validated_token.get('user_id')
            email = validated_token.get('email')
            first_name = validated_token.get('first_name', '')
            last_name = validated_token.get('last_name', '')
            user_role = validated_token.get('user_role', 'employee')
            
            # Debug logging
            print(f"DEBUG JWT: Token claims - user_id: {user_id_from_token}, email: {email}, role: {user_role}")
            
            if not email:
                print("DEBUG JWT: Token does not contain email - INVALID")
                raise InvalidToken('Token does not contain email')
            
            # Try to find user by email (since email is unique)
            try:
                user = User.objects.get(email=email)
                print(f"DEBUG JWT: Found existing user: {user.username} ({user.email})")
            except User.DoesNotExist:
                print(f"DEBUG JWT: User not found, creating new user for email: {email}")
                # Create user if doesn't exist
                # Use a username based on email since username is required
                username = email.split('@')[0]
                
                # Ensure username is unique
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}{counter}"
                    counter += 1
                
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                )
                print(f"DEBUG JWT: Created new user: {user.username}")
                
                # Create corresponding Employee profile if user_role is employee
                if user_role == 'employee':
                    employee, created = Employee.objects.get_or_create(user=user)
                    print(f"DEBUG JWT: Employee profile created: {created}")
            
            return user
            
        except KeyError as e:
            print(f"DEBUG JWT: KeyError - {str(e)}")
            raise InvalidToken('Token contained no recognizable user identification')
        except Exception as e:
            print(f"DEBUG JWT: Exception during user lookup - {str(e)}")
            raise AuthenticationFailed(f'User lookup failed: {str(e)}')
