"""

User URLs

"""

from django.urls import path

from .views import (

    UserProfileView,

    UserProfileUpdateView,

    UserSearchView,

    UserDetailByUsernameView,

)

 

app_name = 'users'

 

urlpatterns = [

    path('profile/', UserProfileView.as_view(), name='profile'),

    path('profile/update/', UserProfileUpdateView.as_view(), name='profile-update'),

    path('search/', UserSearchView.as_view(), name='user-search'),

    path('username/<str:username>/', UserDetailByUsernameView.as_view(), name='user-by-username'),

]

 