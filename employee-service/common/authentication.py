from django.contrib.auth import authenticate

def get_user_from_token(request):
    """
    Extract and validate the JWT token from the request
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None

    token = auth_header.split(' ')[1]
    # Add your JWT token validation logic here
    return token