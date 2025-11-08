"""

User Views - Profile Management

"""

from rest_framework import generics, status

from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response

from rest_framework.views import APIView

from django.contrib.auth import get_user_model

from .serializers import UserProfileSerializer, UserUpdateSerializer, UserListSerializer

 

User = get_user_model()

 

 

class UserProfileView(generics.RetrieveAPIView):

    """

    GET /api/v1/users/profile/

 

    Retrieve the authenticated user's profile information.

    """

    serializer_class = UserProfileSerializer

    permission_classes = [IsAuthenticated]

 

    def get_object(self):

        return self.request.user

 

 

class UserProfileUpdateView(generics.UpdateAPIView):

    """

    PUT/PATCH /api/v1/users/profile/update/

 

    Update the authenticated user's profile.

    Currently only allows updating username.

    """

    serializer_class = UserUpdateSerializer

    permission_classes = [IsAuthenticated]

 

    def get_object(self):

        return self.request.user

 

 

class UserSearchView(generics.ListAPIView):

    """

    GET /api/v1/users/search/?q=username

 

    Search for users by username or phone (for transfers, etc.)

    """

    serializer_class = UserListSerializer

    permission_classes = [IsAuthenticated]

 

    def get_queryset(self):

        query = self.request.query_params.get('q', '')

        if not query:

            return User.objects.none()

 

        # Search by username or phone (partial match)

        return User.objects.filter(

            is_active=True

        ).filter(

            username__icontains=query

        ) | User.objects.filter(

            is_active=True,

            phone__icontains=query

        )[:10]  # Limit to 10 results

 

 

class UserDetailByUsernameView(generics.RetrieveAPIView):

    """

    GET /api/v1/users/username/<username>/

 

    Get basic user info by username (for transfers).

    """

    serializer_class = UserListSerializer

    permission_classes = [IsAuthenticated]

    lookup_field = 'username'

 

    def get_queryset(self):

        return User.objects.filter(is_active=True)

 