from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings

from django.contrib.auth.models import User

fs = FileSystemStorage(location=settings.MEDIA_ROOT)

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, default=None)
    # Add other Doctor-specific fields here, if needed

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)

class PatientImage(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(storage=fs, upload_to='patient_images/')
    eye = models.CharField(max_length=10, choices=[('Left', 'Left'), ('Right', 'Right')])
    date_taken = models.DateField()

class DoctorImageAnalysis(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    patient_image = models.ForeignKey(PatientImage, on_delete=models.CASCADE, related_name='analyses')
    notes = models.TextField(blank=True)
    cdr_points = models.JSONField(blank=True, null=True)
    cdr = models.FloatField()
    description = models.TextField()
    grade = models.IntegerField(choices=[(0, 'Healthy'), (1, 'No Diagnosis'), (2, 'Glaucoma')])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)