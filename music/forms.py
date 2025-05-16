from django import forms
from .models import Audio
from .models import Category

class AudioUploadForm(forms.ModelForm):
    class Meta:
        model = Audio
        fields = ['title', 'audio_file']

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True  # Allow selecting multiple files

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

class BulkAudioUploadForm(forms.Form):
    audio_file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"allow_multiple_selected": True}), required=False
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        help_text="Optional: Assign a category to all uploaded files"
    )
    