from django.urls import path
from . import views


app_name = "agora"

urlpatterns = [
    path('', views.chat, name='agora-index'),
    path('signup', views.signup_view, name='signup'),
    path('signin', views.signin_view, name='signin'),
    path('logout', views.logout_view, name='logout'),
    path('pusher/auth/', views.pusher_auth, name='agora-pusher-auth'),
    path('token/', views.generate_agora_token, name='agora-token'),
    path('call-user/', views.call_user, name='agora-call-user'),
    path('trigger-event/', views.trigger_event, name='trigger'),
]