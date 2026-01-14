from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import redirect

def goto_app(request):
    return redirect('/admin')


def download_app(request):
    pass
