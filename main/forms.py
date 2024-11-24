from django import forms
from user.models import User  # Sử dụng model User của Django
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail  # Thêm hàm gửi email
from django.conf import settings  # Để lấy email mặc định từ settings
from role.models import Role
from user.models import Profile
import random
from django.contrib.auth import authenticate

class EmailForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Nhập email'}))

class ConfirmationCodeForm(forms.Form):
    confirmation_code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập mã xác thực'}))

class RegistrationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Nhập mật khẩu'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Xác nhận mật khẩu'}))
    first_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập họ'}))
    last_name = forms.CharField(max_length=255, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập tên người dùng'}),
        }

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Mật khẩu không khớp")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data["password1"]
        user.set_password(password)
        if commit:
            user.save()
        return user


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label='Email')

class PasswordResetCodeForm(forms.Form):
    code = forms.CharField(label='Authentication Code')
    
class PasswordResetForm(forms.Form):
    new_password = forms.CharField(widget=forms.PasswordInput, label="New password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm new password")

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Password and Confirm password is not match.")


class CustomLoginForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("Invalid login credentials.")
        return cleaned_data