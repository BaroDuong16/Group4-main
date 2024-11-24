from role.models import Role


def create_default_roles():
    role_names = ["Admin", "Instructor", "Student"]

    print("Create role!")
    for role_name in role_names:
        role, created = Role.objects.get_or_create(role_name=role_name, defaults={})

        if created:
            role.save()
            print(f"-- '{role_name}' created!")
        else:
            print(f"-- '{role_name}' existed!")