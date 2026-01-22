# users/views.py
from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.core.cache import cache
from django.conf import settings
import logging

from users.models import User
from users.serializers import UserSerializer

# Set up logging
logger = logging.getLogger(__name__)

def get_cache_key(prefix, identifier=None):
    """Generate consistent cache keys"""
    if identifier:
        return f"{prefix}_{identifier}"
    return prefix


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """
        TEMPORARY: Allow all access for testing
        In production, we will have to set up appropriate permissions
        """
        # lets allow anyone to access for testing
        permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]
    def list(self, request, *args, **kwargs):
        """Cache the list response"""
        cache_key = get_cache_key('user_list_response')
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            logger.info(f"Cache HIT for {cache_key}")
            return Response(cached_data)
        
        logger.info(f"Cache MISS for {cache_key}")
        response = super().list(request, *args, **kwargs)
        
        # Cache the response data
        cache.set(cache_key, response.data, timeout=settings.CACHE_TTL)
        
        return response
    
    def retrieve(self, request, *args, **kwargs):
        """Cache individual user responses"""
        user_id = kwargs.get('pk')
        cache_key = get_cache_key('user_detail', user_id)
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            logger.info(f"Cache HIT for {cache_key}")
            return Response(cached_data)
        
        logger.info(f"Cache MISS for {cache_key}")
        response = super().retrieve(request, *args, **kwargs)
        
        # Cache the individual user data
        cache.set(cache_key, response.data, timeout=settings.CACHE_TTL)
        
        return response
    
    def perform_create(self, serializer):
        """Clear cache when a new user is created"""
        cache.delete(get_cache_key('user_list_response'))
        logger.info("Cache cleared for user_list_response (create)")
        super().perform_create(serializer)
    
    def perform_update(self, serializer):
        """Clear cache when a user is updated"""
        user_id = serializer.instance.id
        
        # Clear individual user cache
        cache.delete(get_cache_key('user_detail', user_id))
        
        # Clear list cache
        cache.delete(get_cache_key('user_list_response'))
        
        logger.info(f"Cache cleared for user_detail_{user_id} and user_list_response (update)")
        super().perform_update(serializer)
    
    def perform_destroy(self, instance):
        """Clear cache when a user is deleted"""
        user_id = instance.id
        
        # Clear individual user cache
        cache.delete(get_cache_key('user_detail', user_id))
        
        # Clear list cache
        cache.delete(get_cache_key('user_list_response'))
        
        logger.info(f"Cache cleared for user_detail_{user_id} and user_list_response (delete)")
        super().perform_destroy(instance)


@api_view(['GET'])
@permission_classes([])
def cache_stats(request):
    """Get cache statistics"""
    from django.core.cache import cache
    
    # Get some basic cache info
    stats = {
        'cache_backend': str(cache),
        'default_timeout': settings.CACHE_TTL,
        'sample_keys': [],
    }
    
    # Try to find our cached keys (this is a simple approach)
    possible_keys = ['user_list_response', 'test_key']
    for key in possible_keys:
        if cache.get(key) is not None:
            stats['sample_keys'].append(key)
    
    return Response(stats)