from module_group.models import Module, ModuleGroup
from role.models import Role

def get_grouped_modules(user, temporary_role_id=None):
    all_modules = Module.objects.all()
    user_modules = all_modules

    if user.is_authenticated:
        if user.is_superuser:
            # Nếu là superuser, kiểm tra role tạm thời
            if temporary_role_id:
                try:
                    user_role = Role.objects.get(role_name=temporary_role_id)
                    user_modules = all_modules.filter(role_modules=user_role).distinct()
                except Role.DoesNotExist:
                    user_modules = Module.objects.none()
            else:
                user_modules = all_modules
        else:
            # Người dùng không phải superuser
            user_profile = getattr(user, 'profile', None)
            user_role = getattr(user_profile, 'role', None)
            if user_role:
                user_modules = all_modules.filter(role_modules=user_role).distinct()
            else:
                user_modules = Module.objects.none()
    
    module_groups = ModuleGroup.objects.all()
    grouped_modules = {}
    for module in user_modules:
        group = module.module_group
        if group not in grouped_modules:
            grouped_modules[group] = []
        grouped_modules[group].append(module)
    
    return module_groups, grouped_modules
