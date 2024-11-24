from role.models import Role
from user.models import User


def create_default_accounts():
    acc_infos = {
        "admin" : {
            "password" : "admin",
            "email" : "admin@gmail.com",
            "full_name" : "Admin Default",
            "role_id" : "Admin",
        },
        "instructor" : {
            "password" : "123",
            "email" : "instructor@gmail.com",
            "full_name" : "Instructor Default",
            "role_id" : "Instructor",
        },
        "student" : {
            "password" : "123",
            "email" : "student@gmail.com",
            "full_name" : "Student Default",
            "role_id" : "Student",
        }
    }

    print("Create user!")
    for key, value in acc_infos.items():
        value['role_id'] = Role.objects.get(role_name= value['role_id']).id
        user, created = User.objects.get_or_create(username=key, defaults=value)

        if created:
            user.set_password(value['password'])
            user.save()
            print(f"-- '{user}' created!")
        else:
            print(f"-- '{user}' existed!")