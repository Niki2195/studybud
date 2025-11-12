from django.urls import path, include
from . import views
from rest_framework import routers
from .api_views import RoomViewSet, MessageViewSet
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register(r'rooms', RoomViewSet)
router.register(r'messages', MessageViewSet)

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('login/', views.loginPage, name='loginPage'),
    path('logout/', views.logoutUser, name='logoutUser'),
    path('register/', views.registerPage, name='registerPage'),

    path('profile/<int:pk>/', views.userProfile, name='user-profile'),
    path('update-profile/', views.updateProfile, name='updateProfile'),

    path('create-room/', views.createRoom, name='createRoom'),
    path('update-room/<int:pk>/', views.updateRoom, name='updateRoom'),
    path('delete-room/<int:pk>/', views.deleteRoom, name='deleteRoom'),
    path('room/<int:pk>/', views.room_detail, name='room_detail'),

    path('delete-message/<int:pk>/', views.deleteMessage, name='deleteMessage'),
    path('activity/', views.activityPage, name='activityPage'),
    path('api/', include(router.urls)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)