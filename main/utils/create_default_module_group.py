from module_group.models import ModuleGroup

def create_default_module_group():
    group_names = ["Training Management", "User Management", "Assessment Management", "Tools"]

    print("Create module_group!")
    for group_name in group_names:
        module_group, created = ModuleGroup.objects.get_or_create(group_name=group_name, defaults={})

        if created:
            module_group.save()
            print(f"-- '{group_name}' created!")
        else:
            print(f"-- '{group_name}' existed!")