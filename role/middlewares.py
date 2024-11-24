# middlewares.py
from django.utils.functional import SimpleLazyObject
from django.contrib.auth.models import Permission
from .models import Role

def role_middleware(get_response):
    def middleware(request):
        temp_role_id = request.session.get('temp_role')
        
        if temp_role_id:
            try:
                role = Role.objects.get(id=temp_role_id)
                request.user.temp_permissions = SimpleLazyObject(lambda: role.permissions.all())
                # Thêm quyền vào user tạm thời
                request.user.user_permissions.add(*role.permissions.all())
            except Role.DoesNotExist:
                request.session.pop('temp_role', None)
        
        response = get_response(request)
        
        # Xóa quyền tạm thời sau khi xử lý request
        if temp_role_id:
            request.user.user_permissions.clear()  # Xóa quyền tạm thời

        return response
    
    return middleware
