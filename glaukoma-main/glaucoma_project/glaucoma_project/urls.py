"""
URL configuration for glaucoma_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('login/', include('glaucoma.urls')),  # Подключение маршрутов из приложения glaucoma
    # #path('success/', vw.success_page, name='success'),
    # path('test/', doctor_list_view, name='template/doctor_list'),
    # #path('login/', auth_views.LoginView.as_view(template_name='/login.html'), name='login'),
    # path('success/', success_page, name='template/success'),  # Страница успеха
    # path('home/', home_page, name='template/home'),
    # path('patients/', patient_list_view, name='patient_list'),
    # path("patients/<int:patient_id>/", views.get_patient_details, name="patient_details"),
    # path("patients/<int:patient_id>/upload_image/", views.upload_patient_image, name="upload_image"),
    # path('patients/<int:patient_id>/images/', views.patient_images_view, name='patient_images'),
    
    path('admin/', admin.site.urls),
    path('', lambda _: redirect('login/')),

    path('', include('authentication.urls')),
    path('', include('glaucoma.urls')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
