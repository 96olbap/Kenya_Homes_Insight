from django.forms import fields
from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')  
    class Meta:
        model = Profile
        fields = ['user','id','profile_photo','bio','phone_number']
        