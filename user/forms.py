from django import forms
from role.models import Role
from user.models import Profile, User, Student
from course.models import UserCourseProgress
from training_program.models import TrainingProgram


class UserForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=True)
    profile_picture_url = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter profile picture URL'}))
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your bio'}), required=False)
    interests = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your interests'}), required=False)
    learning_style = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your learning style'}), required=False)
    preferred_language = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your preferred language'}), required=False)
    training_programs = forms.ModelMultipleChoiceField(queryset=TrainingProgram.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    student = forms.ModelChoiceField(queryset=Student.objects.all(), required=False)
    student_code = forms.CharField(max_length=20, required=False) 
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password'}),
        required=False
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password'}),
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2', 'profile_picture_url', 'bio', 'interests', 'learning_style', 'preferred_language', 'training_programs', 'student','student_code']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('A user with that username already exists.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if not self.instance.pk and (not password1 or not password2):
            raise forms.ValidationError("Password is required when creating a new user.")

        if password1 and password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if self.cleaned_data.get('password1'):
            user.set_password(self.cleaned_data['password1'])
        elif self.instance.pk:
            current_user = User.objects.get(pk=self.instance.pk)
            user.password = current_user.password

        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data['role']
            profile.profile_picture_url = self.cleaned_data.get('profile_picture_url')
            profile.bio = self.cleaned_data.get('bio', '')
            profile.interests = self.cleaned_data.get('interests', '')
            profile.learning_style = self.cleaned_data.get('learning_style', '')
            profile.preferred_language = self.cleaned_data.get('preferred_language', '')
            profile.student = self.cleaned_data.get('student')  
            profile.save()

        return user


class UserEditForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=True)
    profile_picture_url = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Enter profile picture URL'}))
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your bio'}), required=False)
    interests = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your interests'}), required=False)
    learning_style = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your learning style'}), required=False)
    preferred_language = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your preferred language'}), required=False)
    training_programs = forms.ModelMultipleChoiceField(queryset=TrainingProgram.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)
    student = forms.ModelChoiceField(queryset=Student.objects.all(), required=False)
    student_code = forms.CharField(max_length=20, required=False) 
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'profile_picture_url', 'bio', 'interests', 'learning_style', 'preferred_language', 'training_programs', 'student','student_code']


class ExcelImportForm(forms.Form):
    excel_file = forms.FileField()


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['role_name']
        

        

class UserCourseProgressForm(forms.ModelForm):
    class Meta:
        model = UserCourseProgress
        fields = ['user', 'course', 'progress_percentage']

