import os
from django.contrib import admin
from django import forms
from django.urls import path
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from .models import Audio, Category
from django.contrib import admin
from django.utils.text import slugify
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import Audio, Category
from .forms import BulkAudioUploadForm
from taggit.models import Tag
import os



def generate_unique_slug(title):
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    while Audio.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug


class AudioAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "uploaded_at", "likes")
    search_fields = ("title",)
    list_filter = ("category", "uploaded_at")

    def bulk_upload_view(self, request):
        if request.method == 'POST':
            form = BulkAudioUploadForm(request.POST, request.FILES)
            
            if form.is_valid():
                files = request.FILES.getlist('audio_files')
                category = form.cleaned_data.get('category')
                uploaded_files_count = 0
                for f in files:
                    title = " ".join(os.path.splitext(f.name)[0].replace("_", " ").replace("-", " ").split())
                    slug = generate_unique_slug(title)
                    file_path = default_storage.save(f"audios/{f.name}", ContentFile(f.read()))
                    audio = Audio.objects.create(title=title, slug=slug, audio_file=file_path, category=category)
                    tag_list = title.lower().split()
                    audio.tags.add(*tag_list)
                self.message_user(request, f"Successfully uploaded {len(files)} audio files.")
                return redirect("..")
        else:
            form = BulkAudioUploadForm()

        return render(request, "admin/bulk_audio_upload.html", {"form": form})

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('bulk-upload/', self.admin_site.admin_view(self.bulk_upload_view), name='audio-bulk-upload')
        ]
        return custom_urls + urls

admin.site.register(Audio, AudioAdmin)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}