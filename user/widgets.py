from import_export import widgets
from django.contrib.auth.hashers import make_password

class PasswordWidget(widgets.Widget):
    def clean(self, value, row=None, *args, **kwargs):
        if value:
            return make_password(value)  
        return None