from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def get_authenticated_client(user=None):
    """
    Returns an authenticated APIClient instance.
    
    Args:
        user: User instance to authenticate with. If None, creates a new user.
        
    Returns:
        An authenticated APIClient instance.
    """
    if user is None:
        user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
    
    client = APIClient()
    
    # Get JWT token
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    return client, user

def force_authenticate_client(client, user):
    """
    Force authenticates a client with a user without using JWT.
    Useful for testing when JWT is not available or not working.
    
    Args:
        client: APIClient instance
        user: User instance to authenticate with
        
    Returns:
        The authenticated client
    """
    client.force_authenticate(user=user)
    return client