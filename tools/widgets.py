# widgets.py
from django.forms.widgets import ClearableFileInput
from django.forms.widgets import CheckboxInput

FILE_INPUT_CONTRADICTION = object()

class ClearableMultipleFilesInput(ClearableFileInput):
    def value_from_datadict(self, data, files, name):
        upload = files.getlist(name)

        if not self.is_required and CheckboxInput().value_from_datadict(
                data, files, self.clear_checkbox_name(name)):
            if upload:
                return FILE_INPUT_CONTRADICTION
            return False
        return upload
