from django.urls import path, include
from rest_framework.routers import DefaultRouter
#from .views import DoctorViewSet, PatientViewSet, PatientImageViewSet, DoctorImageAnalysisViewSet, LoginView, DoctorLoginView
#from .views import login_api
from django.contrib.auth import views as auth_views
from .views import doctor_list_view, home_page, \
    patient_list_view, get_patient_details, upload_patient_image, patient_images_view, \
    image_analysis, auto_cdr_view, auto_segmentation_view, save_analysis_view


#router = DefaultRouter()
#router.register(r'doctors', DoctorViewSet)
#router.register(r'patients', PatientViewSet)
#router.register(r'patient-images', PatientImageViewSet)
#router.register(r'image-analyses', DoctorImageAnalysisViewSet)

urlpatterns = [
    #path('login/', views.LoginView.as_view(), name='login'),
    #path('login/', DoctorLoginView.as_view(), name='login'),  # Страница логина
    #path('login/', login_api, name='login_api'),  # API для логина
    #path('', views.home, name='glaucoma-home')
    #path('', DoctorLoginView.as_view(), name='doctor_login'),

    # path('', doctor_login_view, name='doctor_login'),
    # path('success/', success_page, name='template/success'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('test/', doctor_list_view, name='template/doctor_list'),
    
    path('glaucoma/home/', home_page, name='home'),
    path('glaucoma/patients/', patient_list_view, name='patient_list'),
    path('glaucoma/patients/<int:patient_id>/', get_patient_details, name="patient_details"),
    path('glaucoma/patients/<int:patient_id>/upload_image/', upload_patient_image, name="upload_image"),
    path('glaucoma/patients/<int:patient_id>/images/', patient_images_view, name='patient_images'),

    path('glaucoma/image/analysis/<int:image_id>', image_analysis, name='image_analysis'),
    path('glaucoma/image/auto_cdr/<int:image_id>/', auto_cdr_view, name='auto_cdr'),
    path('glaucoma/image/auto_segmentation/<int:image_id>/', auto_segmentation_view, name='auto_segmentation'),
    path('glaucoma/image/save_analysis/<int:image_id>/', save_analysis_view, name="save_analysis"),
    ]