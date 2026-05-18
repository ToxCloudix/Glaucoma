from rest_framework import serializers
from .models import Doctor, Patient, PatientImage, DoctorImageAnalysis

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = '__all__'

class PatientSerializer(serializers.ModelSerializer):
    images = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Patient
        fields = '__all__'

class PatientImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        if obj.image:
            return obj.image.url
        return None

    class Meta:
        model = PatientImage
        fields = '__all__'

class DoctorImageAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorImageAnalysis
        fields = '__all__'