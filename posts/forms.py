from django import forms
from .models import Post, Comment
from django.forms.widgets import Textarea


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'group', 'text', 'image']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
