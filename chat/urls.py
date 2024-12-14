from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('welcome_authenticated/', views.welcome_authenticated, name='welcome_authenticated'),
    path('welcome_non_authenticated/', views.welcome_non_authenticated, name='welcome_non_authenticated'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('delete_discussion/<int:discussion_id>/', views.delete_discussion, name='delete_discussion'),
]
