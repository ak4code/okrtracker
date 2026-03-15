from django.urls import include, path

from core.api.views import (
    CurrentUserAPIView,
    JWTLoginAPIView,
    JWTRefreshAPIView,
    RoleDetailAPIView,
    RoleListAPIView,
    TeamDetailAPIView,
    TeamListAPIView,
    UserDetailAPIView,
    UserListAPIView,
)

app_name = 'core_api'

auth_urlpatterns = [
    path('jwt/login/', JWTLoginAPIView.as_view(), name='jwt-login'),
    path('jwt/refresh/', JWTRefreshAPIView.as_view(), name='jwt-refresh'),
    path('me/', CurrentUserAPIView.as_view(), name='current-user'),
]

urlpatterns = [
    path('auth/', include(auth_urlpatterns)),
    path('roles/', RoleListAPIView.as_view(), name='role-list'),
    path('roles/<int:role_id>/', RoleDetailAPIView.as_view(), name='role-detail'),
    path('teams/', TeamListAPIView.as_view(), name='team-list'),
    path('teams/<int:team_id>/', TeamDetailAPIView.as_view(), name='team-detail'),
    path('users/', UserListAPIView.as_view(), name='user-list'),
    path('users/<int:user_id>/', UserDetailAPIView.as_view(), name='user-detail'),
]
