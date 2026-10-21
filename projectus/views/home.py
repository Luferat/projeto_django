from django.shortcuts import render
from django.conf import settings
from projectus.models import Post


def home(request):

    posts = Post.objects.filter(
        is_active=True, is_deleted=False
    ).order_by('-created_at')

    contexto = {
        'tag_title': f'{settings.SITENAME}',
        'posts': posts
    }
    return render(
        request,
        'projectus/home.html',
        contexto
    )
