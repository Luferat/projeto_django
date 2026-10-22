from django.shortcuts import get_object_or_404, redirect, render
from projectus.models import Post
from django.conf import settings
from ..forms import CommentForm


def post_view(request, id):

    # Obtém o post solicitado pelo ID
    post = get_object_or_404(Post, id=id)

    # Trata nome do autor
    if post.user.first_name and post.user.last_name:
        author_name = f'{post.user.first_name} {post.user.last_name}'
    elif post.user.first_name:
        author_name = post.user.first_name
    else:
        author_name = post.user.username

    # Obtém os posts do mesmo autor aleatóriamente
    posts = Post.objects.filter(
        user=post.user,
        is_active=True,
        is_deleted=False
    ).exclude(
        # Excluindo o post atual
        id=post.id
    ).order_by('?')[:3]  # Fatia somente 3 posts

    # Processa o comentário enviado
    if request.method == 'POST':
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

    return render(
        request,
        'projectus/post_view.html',
        {
            'tag_title': f'{settings.SITENAME} - {post.title}',
            'post': post,  # Post original
            'posts': posts,  # Posts do autor
            'author_name': author_name,  # Nome do autor do post, ajustado
            'form': form,  # Campos do formulário de comentários
            'comments': comments, # Comentários existentes
        }
    )
