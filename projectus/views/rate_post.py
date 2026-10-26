from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from projectus.models import Post, Rating


@login_required
@require_POST
def rate_post(request, id):
    """Registra (ou altera) o voto do usuário logado em um post."""

    post = get_object_or_404(Post.objects.visible(), id=id)

    # Aceita somente números inteiros de 1 a 5
    try:
        score = int(request.POST.get('score', ''))
    except ValueError:
        score = 0

    if 1 <= score <= 5:
        # Um voto por usuário em cada post: se já existir, atualiza a nota
        Rating.objects.update_or_create(
            post=post,
            user=request.user,
            defaults={'score': score},
        )

    return redirect('post_view', id=post.id)
