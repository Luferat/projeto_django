from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q, Value
from django.db.models.functions import Concat
from django.shortcuts import render

from projectus.models import Post

POSTS_POR_PAGINA = 6

# Onde procurar o texto digitado
CAMPOS_BUSCA = {
    'todos': 'Título e autor',
    'titulo': 'Título',
    'autor': 'Autor',
}

# Ordenação (a segunda coluna desempata posts criados no mesmo instante)
ORDENACOES = {
    'recentes': ('-created_at', '-id'),
    'antigos': ('created_at', 'id'),
}


def home(request):

    q = request.GET.get('q', '').strip()

    campo = request.GET.get('campo', 'todos')
    if campo not in CAMPOS_BUSCA:
        campo = 'todos'

    ordem = request.GET.get('ordem', 'recentes')
    if ordem not in ORDENACOES:
        ordem = 'recentes'

    # Obtém os posts filtrados por `is_active`, `is_deleted`,
    # com a média de estrelas e o nome completo do autor para a busca
    posts = Post.objects.visible().with_ratings().select_related(
        'user'
    ).annotate(
        author_fullname=Concat(
            'user__first_name', Value(' '), 'user__last_name'
        )
    )

    # Cada palavra digitada precisa aparecer no campo escolhido
    # (ex.: "maria django" acha posts de Maria com "Django" no título)
    for termo in q.split():
        no_titulo = Q(title__icontains=termo)
        no_autor = (
            Q(author_fullname__icontains=termo)
            | Q(user__username__icontains=termo)
        )

        if campo == 'titulo':
            posts = posts.filter(no_titulo)
        elif campo == 'autor':
            posts = posts.filter(no_autor)
        else:
            posts = posts.filter(no_titulo | no_autor)

    posts = posts.order_by(*ORDENACOES[ordem])

    # Paginação
    paginator = Paginator(posts, POSTS_POR_PAGINA)
    page_obj = paginator.get_page(request.GET.get('page'))

    # Parâmetros atuais (sem `page`) para manter a busca nos links de página
    params = request.GET.copy()
    params.pop('page', None)

    return render(
        request,
        'projectus/home.html',
        {
            'tag_title': f'{settings.SITENAME}',
            'posts': page_obj,
            'page_obj': page_obj,
            'total': paginator.count,
            'q': q,
            'campo': campo,
            'ordem': ordem,
            'campos_busca': CAMPOS_BUSCA,
            'query_string': params.urlencode(),
        }
    )
