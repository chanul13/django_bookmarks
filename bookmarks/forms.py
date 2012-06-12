import re  # Regular expression library
from django.contrib.auth.models import User
from django import forms

class RegistrationForm(forms.Form):
    
    # Form fields
    username = forms.CharField(label=u'Username', max_length=30)
    email = forms.EmailField(label=u'Email')
    password1 = forms.CharField(
        label=u'Password', 
        widget=forms.PasswordInput()
    )
    password2 = forms.CharField(
        label=u'Password (Again)', 
        widget=forms.PasswordInput()
    )
    
    # All custom validation methods start with "clean_"
    def clean_password2(self):
        # All data which passed form validation are accessible
        # through the "self.cleaned_data" dictionary
        if 'password1' in self.cleaned_data:
            password1 = self.cleaned_data['password1']
            password2 = self.cleaned_data['password2']
            if password1 == password2:
                return password2
        raise forms.ValidationError('Passwords do not match')

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.search(r'^\w+$', username):
            raise forms.ValidationError('Username can only contain '
                                        'alphanumeric characters and underscores.')
        try:
            User.objects.get(username = username)
        except User.DoesNotExist:
            # If the username doesn't exist (i.e. it's not already
            # taken and it contains valid chars, then it's a valid
            # username
            return username
        raise forms.ValidationError('Username is already taken.')

    def clean_email(self):
        email = self.cleaned_data['email']
        username = self.cleaned_data['username']

        try:
            User.objects.get(email = email)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError('Email is already in use by another user.')

class BookmarkSaveForm(forms.Form):

    # Form fields
    url = forms.URLField(
        label = u'URL',
        widget = forms.TextInput(attrs = {'size': 64})
    )
    title =  forms.CharField(
        label = u'Title',
        widget = forms.TextInput(attrs = {'size': 64})
    )
    tags = forms.CharField(
        label=u'Tags',
        required = False,
        widget = forms.TextInput(attrs = {'size': 64})
    )

class SearchForm(forms.Form):
    query = forms.CharField(
        label = u'Enter a keyword to search for',
        widget = forms.TextInput(attrs = { 'size': 32 })
    )
