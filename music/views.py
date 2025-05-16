from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from mutagen import File as MutagenFile
from django.http import FileResponse
from .models import Audio
from django.core.paginator import Paginator
import os
from django.http import FileResponse, Http404

def audio_list(request):
    tag = request.GET.get('tag')
    
    if tag:
        audios = Audio.objects.filter(tags__name__in=[tag])
    else:
        audios = Audio.objects.all()

    paginator = Paginator(audios.order_by('-uploaded_at'), 20)  # Show 10 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'music/index.html', {
        'page_obj': page_obj,
        'tag': tag,
    })

def like_audio(request, audio_id):
    audio = get_object_or_404(Audio, id=audio_id)
    audio.likes += 1
    audio.save()
    return redirect('audio_detail', slug=audio.slug)


def audio_detail(request, slug):
    audio = get_object_or_404(Audio, slug=slug)

    # Extract metadata dynamically (optional if stored in DB)
    try:
        metadata = MutagenFile(audio.audio_file.path)
        duration = round(metadata.info.length, 2) if metadata.info.length else None
        bitrate = metadata.info.bitrate if hasattr(metadata.info, 'bitrate') else None
        filesize = os.path.getsize(audio.audio_file.path)

        genre = metadata.tags.get('TCON', [None])[0] if metadata.tags and metadata.tags.get('TCON') else 'sound effects'
        artist = metadata.tags.get('TPE1', [None])[0] if metadata.tags and metadata.tags.get('TPE1') else 'www.memehive.net'
        album = metadata.tags.get('TALB', [None])[0] if metadata.tags and metadata.tags.get('TALB') else 'memehive'

    except Exception as e:
        duration = bitrate = filesize = genre = artist = None
        album = 'memehive'
        print("Metadata error:", e)

    context = {
        'audio': audio,
        'duration': duration,
        'bitrate': bitrate,
        'filesize': filesize,
        'genre': genre,
        'artist': artist,
        'album': album,
    }
    return render(request, 'music/audio_detail.html', context)

def download_audio(request, slug):
    audio = get_object_or_404(Audio, slug=slug)
    
    # Increment download count
    audio.downloads += 1
    audio.save()

    # Serve the file
    audio_path = audio.audio_file.path
    if os.path.exists(audio_path):
        response = FileResponse(open(audio_path, 'rb'), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(audio_path)}"'
        return response
    else:
        raise Http404("Audio file not found.")