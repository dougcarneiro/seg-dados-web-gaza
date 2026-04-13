from django.urls import path

from . import views

app_name = 'refugees'

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path(
        'signup/check-password/',
        views.password_strength_preview,
        name='password_strength_preview',
    ),
    path('login/', views.EmailLoginView.as_view(), name='login'),
    path('logout/', views.AppLogoutView.as_view(), name='logout'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/delete/', views.profile_delete_confirm, name='profile_delete_confirm'),
    path('profile/delete/definitivo/', views.profile_delete, name='profile_delete'),
]
