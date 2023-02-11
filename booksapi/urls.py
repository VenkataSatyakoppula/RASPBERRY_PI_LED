from .views import VerifyEmail,PasswordChange,PasswordTokenCheckAPI,BooksFilter,UserUpdateView,UserDeleteView,Booksview,pi_light_on,pi_light_off,GetUser,UserRegistration,RequestPasswordReset
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
app_name = 'booksapi'

router = DefaultRouter()
router.register('',Booksview,basename='books')

urlpatterns = [
    path('light-on/<int:pk>/',pi_light_on,name="light-on"),
    path('light-off/<int:pk>/',pi_light_off,name="light-off"),
    path('get_tokens/',TokenObtainPairView.as_view(),name='token_pair'),
    path('get_user/<int:pk>/',GetUser.as_view(),name='user-detail'),
    path('delete_user/<int:pk>/',UserDeleteView.as_view(),name="user-delete"),
    path('update_user/<int:pk>/', UserUpdateView.as_view(), name='user-update'),
    path('refresh_token/',TokenRefreshView.as_view(),name="token_refresh"),
    path('verify_token/',TokenVerifyView.as_view(),name="token_verify"),
    path("register/",UserRegistration.as_view(),name='register'),
    path('password-reset/<uidb64>/<token>/',PasswordTokenCheckAPI.as_view(),name="password-reset"),
    path('password-reset/',PasswordTokenCheckAPI.as_view(),name="password-reset-patch"),
    path('password-change/',PasswordChange.as_view(),name='change-password'),      
    path('email-verify/',VerifyEmail.as_view(),name="email-verify"),                                                                                              
    path("forgot-password/",RequestPasswordReset.as_view(),name="forgot-password"),
    path("search/",BooksFilter.as_view(),name='booksearch'),
]
urlpatterns += router.urls
