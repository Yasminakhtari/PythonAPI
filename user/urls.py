from django.urls import path
from .views import UserListCreateView, UserDetailView

urlpatterns = [
    path('user/', UserListCreateView.as_view(), name='user-list-create'),
    path('user/<int:pk>/', UserDetailView.as_view(), name='user-detail'),
]