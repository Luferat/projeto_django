from django.shortcuts import render
from django.conf import settings
from projectus.models import Post


def home(request):

    # Obtém os posts ordenados pelos mais recentes
    # filtrados por `is_active`, `is_deleted`
    posts = Post.objects.filter(
        is_active=True,
        is_deleted=False
    ).order_by('-created_at')

    # Total de registro
    total = len(posts)

    return render(
        request,
        'projectus/home.html',
        {
            'tag_title': f'{settings.SITENAME}',
            'posts': posts,
            'total': total
        }
    )
