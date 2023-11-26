from django import forms
from .models import Comment


class CommentForm(forms.ModelForm):
    # Add an integer field for captcha input
    captcha = forms.IntegerField()  # new
    class Meta:
        model = Comment
        #fields = ("comment",)
        fields = ("comment","captcha",) # new