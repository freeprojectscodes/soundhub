from django.db import models
from django.utils.text import slugify
from taggit.managers import TaggableManager
from ckeditor.fields import RichTextField
from mutagen import File as MutagenFile
from mutagen.easyid3 import EasyID3
import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.core.files.base import ContentFile

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Audio(models.Model):
    title = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    audio_file = models.FileField(upload_to='audios/')
    featured_image = models.ImageField(upload_to='featured_image/', blank=True, null=True)
    description = RichTextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    likes = models.PositiveIntegerField(default=0)
    tags = TaggableManager(blank=True)
    artist = models.CharField(max_length=255, blank=True, default='www.memehive.net')
    album = models.CharField(max_length=200, blank=True, default='memehive')
    genre = models.CharField(max_length=100, blank=True, default='sound effects')
    bitrate = models.IntegerField(blank=True, null=True)  # in bps
    filesize = models.IntegerField(blank=True, null=True)  # in bytes
    duration = models.FloatField(blank=True, null=True)  # in seconds
    downloads = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        # Auto title from filename
        if not self.title:
            base = os.path.basename(self.audio_file.name)
            name, ext = os.path.splitext(base)
            self.title = name.replace('_', ' ').title()

        # Auto slug
        if not self.slug:
            self.slug = slugify(self.title)

        # Save first to access audio_file.path
        super().save(*args, **kwargs)

        # Auto-generate featured image
        if self.audio_file and not self.featured_image:
            image = self._generate_featured_image(self.title, self.artist)
            self.featured_image.save(f"{self.slug}_featured.png", image, save=False)

        # Extract audio metadata
        try:
            audio_file_path = self.audio_file.path
            audio = MutagenFile(audio_file_path, easy=True)

            if audio is not None:
                self.duration = round(audio.info.length, 2) if hasattr(audio.info, 'length') else None
                self.bitrate = audio.info.bitrate if hasattr(audio.info, 'bitrate') else None
                self.filesize = os.path.getsize(audio_file_path)

                if isinstance(audio, EasyID3):
                    self.artist = audio.get("artist", [self.artist])[0]
                    self.album = audio.get("album", [self.album])[0]
                    self.genre = audio.get("genre", [self.genre])[0]
                else:
                    tags = audio.tags
                    if tags:
                        self.artist = tags.get('\xa9ART', [self.artist])[0]
                        self.album = tags.get('\xa9alb', [self.album])[0]
                        self.genre = tags.get('\xa9gen', [self.genre])[0]

        except Exception as e:
            print("Metadata extraction error:", e)

        # Auto-generate tags
        if self.tags.count() == 0:
            tag_words = self.title.lower().split()
            self.tags.add(*tag_words)

        # Final save
        super().save(update_fields=[
            'title', 'slug', 'duration', 'bitrate',
            'filesize', 'artist', 'album', 'genre', 'featured_image'
        ])

    def _generate_featured_image(self, title, artist=None):
        from PIL import Image, ImageDraw, ImageFont
        from io import BytesIO
        from django.core.files.base import ContentFile
        import random

        width, height = 640, 640
        background_color = (17, 24, 39)
        text_color = (255, 255, 255)
        branding_color = (147, 197, 253)

        img = Image.new("RGB", (width, height), background_color)
        draw = ImageDraw.Draw(img)

        try:
            font_title = ImageFont.truetype("arial.ttf", 40)
            font_small = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            font_title = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Combine title and artist
        text = title
        if artist:
            text += f"\nby {artist}"

        # Split lines and measure
        text_lines = text.split('\n')
        total_height = 0
        line_sizes = []

        for line in text_lines:
            bbox = draw.textbbox((0, 0), line, font=font_title)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            line_sizes.append((w, h))
            total_height += h

        # Draw text near top (1/4 vertical position)
        y = int(height * 0.15)
        for i, line in enumerate(text_lines):
            w, h = line_sizes[i]
            x = (width - w) // 2
            draw.text((x, y), line, fill=text_color, font=font_title)
            y += h

        # Draw waveform in lower half
        num_bars = 60
        bar_width = width // num_bars
        for i in range(num_bars):
            x = i * bar_width
            bar_height = random.randint(40, 180)
            center_y = int(height * 0.65)
            y_top = center_y - bar_height // 2
            y_bottom = center_y + bar_height // 2
            draw.rectangle([x + 2, y_top, x + bar_width - 2, y_bottom], fill=(255, 255, 255, 180))

        # Branding at bottom-right
        branding_text = "memehive.net"
        bbox = draw.textbbox((0, 0), branding_text, font=font_small)
        branding_width = bbox[2] - bbox[0]
        branding_height = bbox[3] - bbox[1]

        draw.text(
            (width - branding_width - 20, height - branding_height - 20),
            branding_text,
            fill=branding_color,
            font=font_small
        )

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        return ContentFile(buffer.getvalue(), name="featured.png")




    def formatted_duration(self):
        if self.duration:
            mins = int(self.duration) // 60
            secs = int(self.duration) % 60
            return f"{mins}:{secs:02d}"
        return "-"

    def __str__(self):
        return self.title
