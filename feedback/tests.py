#from django.test import TestCase

from role.models import Role

try:
    # Retrieve the Role instance where role_name is 'Instructor'
    instructor_role = Role.objects.get(role_name='Instructor')
except Role.DoesNotExist:
    print("Role 'Instructor' not found.")
