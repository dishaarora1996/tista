from rest_framework import serializers
from .models import CustomUser

class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = ['full_name', 'gender']

        extra_kwargs = {
            'full_name': {'required': True},
            'gender': {'required': True}
        }

    def update(self, instance, validated_data):
        # Update user fields
        instance.full_name = validated_data.get('full_name', instance.full_name)
        instance.gender = validated_data.get('gender', instance.gender)
        instance.save()
        return instance