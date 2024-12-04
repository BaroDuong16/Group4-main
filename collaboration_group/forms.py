from django import forms
from .models import CollaborationGroup, GroupMember, GroupFeedback, MemberFeedback
from django.contrib.auth import get_user_model

User = get_user_model()

class CollaborationGroupForm(forms.ModelForm):
    class Meta:
        model = CollaborationGroup
        fields = ['group_name', 'courses']  # Update to 'courses'
        widgets = {
            'group_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter group name'
            }),
            'courses': forms.SelectMultiple(attrs={
                'class': 'form-control',  # Use the form-control class for styling
                'placeholder': 'Select courses',  # Placeholder text for single select
            }),
        }

class GroupMemberForm(forms.ModelForm):
    user = forms.ModelChoiceField(queryset=User.objects.none(), label="Select User")  # Set an empty queryset initially

    class Meta:
        model = GroupMember
        fields = ['user']  # Only include the user field
        widgets = {
            'user': forms.Select(attrs={
                'class': 'form-control',  # Bootstrap class for styling
            }),
        }

    def __init__(self, *args, **kwargs):
        user_queryset = kwargs.pop('user_queryset', User.objects.none())  # Extract user_queryset if provided
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = user_queryset

class GroupFeedbackForm(forms.ModelForm):
    class Meta:
        model = GroupFeedback
        fields = ['group_engagement', 'collaboration_quality', 'goal_achievement', 'comments']
        widgets = {
            'group_engagement': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'collaboration_quality': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'goal_achievement': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class MemberFeedbackForm(forms.ModelForm):
    class Meta:
        model = MemberFeedback
        fields = ['member', 'teamwork', 'reliability', 'leadership', 'communication', 'comments']
        widgets = {
            'member': forms.Select(attrs={'class': 'form-control'}),
            'teamwork': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'reliability': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'leadership': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'communication': forms.RadioSelect(choices=[(i, str(i)) for i in range(1, 6)]),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        group = kwargs.pop('group', None)
        super().__init__(*args, **kwargs)
        if group:
            # Filter the member field queryset to include only users who are members of the group
            self.fields['member'].queryset = User.objects.filter(group_memberships__group=group)