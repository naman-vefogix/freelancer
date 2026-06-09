from rest_framework import serializers
from .models import Job,Applications

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
        'id',
        'title',
        'description',
        'created_at'
        ]
        read_only_fields = [
            'id',
            'created_at'
        ]
    
class ApplicatonSerializer(serializers.ModelSerializer):
    freelancer_username = serializers.SerializerMethodField()
    def get_freelancer_username(self, obj):
        return obj.freelancer.username if obj.freelancer else None
    class Meta:
        model = Applications
        fields = "__all__"
        read_only_fields = ['job', 'freelancer']
