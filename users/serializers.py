# users/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'password', 'user_type', 'phone_number',
            'first_name', 'last_name', 'is_active', 'date_joined',
            'created_at', 'updated_at', 'is_staff', 'is_superuser'
        ]
        read_only_fields = [
            'id', 'date_joined', 'created_at', 'updated_at',
            'is_staff', 'is_superuser'
        ]
    
    def create(self, validated_data):
        # Hash the password before saving
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        # Handle password update
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        
        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance