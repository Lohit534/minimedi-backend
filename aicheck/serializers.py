from rest_framework import serializers
from .models import SymptomLog

class SymptomLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SymptomLog
        fields = ['title', 'date_logged']