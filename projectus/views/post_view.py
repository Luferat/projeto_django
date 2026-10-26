from django.shortcuts import get_object_or_404, redirect, render
from projectus.models import Post
from django.conf import settings
from ..forms import CommentForm


def post_view(request, id):

    # Obtém o post solicitado pelo ID, já com a média e o total de votos
    post = get_object_or_404(
        Post.objects.visible().with_ratings().select_related('user'),
        id=id
    )

    # Nome do autor, ajustado (nome completo, nome ou usuário)
    author_name = post.author_name

    # Obtém os posts do mesmo autor aleatóriamente
    posts = Post.objects.visible().with_ratings().filter(
        user=post.user
    ).exclude(
        # Excluindo o post atual
        id=post.id
    ).order_by('?')[:3]  # Fatia somente 3 posts

    # Processa o comentário enviado
    if request.method == 'POST':

        # Somente usuários logados podem comentar
        if not request.user.is_authenticated:
            return redirect(f'{settings.LOGIN_URL}?next={request.path}')

        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()

            return redirect('post_view', id=post.id)
    else:
        form = CommentForm()

    # Obtém comentários existentes
    comments = post.comments.filter(
        is_active=True,
        is_deleted=False
    ).order_by('-created_at')

    # Nota que o usuário logado já deu a este post (None se não votou)
    user_score = None
    if request.user.is_authenticated:
        user_score = post.ratings.filter(
            user=request.user
        ).values_list('score', flat=True).first()

    return render(
        request,
        'projectus/post_view.html',
        {
            'tag_title': f'{settings.SITENAME} - {post.title}',
            'post': post,  # Post original
            'posts': posts,  # Posts do autor
            'author_name': author_name,  # Nome do autor do post, ajustado
            'form': form,  # Campos do formulário de comentários
            'comments': comments,  # Comentários existentes
            'user_score': user_score,  # Voto do usuário logado
            'star_values': [5, 4, 3, 2, 1],  # Ordem usada pelo CSS das estrelas
        }
    )
