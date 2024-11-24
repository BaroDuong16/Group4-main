# fields.py
from django.core.exceptions import ValidationError
from django.forms.fields import FileField
from .widgets import ClearableMultipleFilesInput
from .widgets import FILE_INPUT_CONTRADICTION

class MultipleFilesField(FileField):
    widget = ClearableMultipleFilesInput

    def clean(self, data, initial=None):
        if data is FILE_INPUT_CONTRADICTION:
            raise ValidationError(self.error_messages['contradiction'], code='contradiction')
        if data is False:
            if not self.required:
                return False
            data = None
        if not data and initial:
            return initial
        return data
