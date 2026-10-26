from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from projectus.models import Comment, Post, Rating

User = get_user_model()


def criar_post(user, title, dias_atras=0, **extra):
    """Cria um post "publicado" há `dias_atras` dias."""
    post = Post.objects.create(
        user=user,
        title=title,
        summary='Resumo',
        thumbnail='https://example.com/imagem.jpg',
        textbody='Texto do post',
        **extra
    )
    # `created_at` é automático; ajustamos depois para testar a ordenação
    Post.objects.filter(pk=post.pk).update(
        created_at=timezone.now() - timedelta(days=dias_atras)
    )
    post.refresh_from_db()
    return post


class RatingTests(TestCase):

    def setUp(self):
        self.autor = User.objects.create_user('autor', password='x12345678')
        self.leitor = User.objects.create_user('leitor', password='x12345678')
        self.post = criar_post(self.autor, 'Meu post')
        self.url = reverse('rate_post', kwargs={'id': self.post.id})

    def test_visitante_e_enviado_para_o_login(self):
        resposta = self.client.post(self.url, {'score': 5})

        self.assertRedirects(
            resposta,
            f'/accounts/login/?next={self.url}',
            fetch_redirect_response=False
        )
        self.assertEqual(Rating.objects.count(), 0)

    def test_usuario_logado_vota(self):
        self.client.force_login(self.leitor)

        resposta = self.client.post(self.url, {'score': 4})

        self.assertRedirects(
            resposta,
            reverse('post_view', kwargs={'id': self.post.id}),
            fetch_redirect_response=False
        )
        voto = Rating.objects.get(post=self.post, user=self.leitor)
        self.assertEqual(voto.score, 4)

    def test_votar_de_novo_altera_a_nota(self):
        self.client.force_login(self.leitor)

        self.client.post(self.url, {'score': 4})
        self.client.post(self.url, {'score': 2})

        self.assertEqual(Rating.objects.count(), 1)
        self.assertEqual(Rating.objects.get().score, 2)

    def test_notas_invalidas_sao_ignoradas(self):
        self.client.force_login(self.leitor)

        for valor in ['0', '6', '-1', 'abc', '']:
            self.client.post(self.url, {'score': valor})

        self.assertEqual(Rating.objects.count(), 0)

    def test_get_nao_e_permitido(self):
        self.client.force_login(self.leitor)

        resposta = self.client.get(self.url)

        self.assertEqual(resposta.status_code, 405)

    def test_post_excluido_nao_recebe_voto(self):
        self.post.is_deleted = True
        self.post.save()
        self.client.force_login(self.leitor)

        resposta = self.client.post(self.url, {'score': 5})

        self.assertEqual(resposta.status_code, 404)
        self.assertEqual(Rating.objects.count(), 0)

    def test_media_e_total_de_votos(self):
        Rating.objects.create(post=self.post, user=self.autor, score=5)
        Rating.objects.create(post=self.post, user=self.leitor, score=2)

        post = Post.objects.with_ratings().get(pk=self.post.pk)

        self.assertAlmostEqual(float(post.avg_rating), 3.5)
        self.assertEqual(post.votes_count, 2)

    def test_post_sem_votos(self):
        post = Post.objects.with_ratings().get(pk=self.post.pk)

        self.assertIsNone(post.avg_rating)
        self.assertEqual(post.votes_count, 0)

    def test_pagina_do_post_mostra_a_nota_do_usuario(self):
        Rating.objects.create(post=self.post, user=self.leitor, score=3)
        self.client.force_login(self.leitor)

        resposta = self.client.get(
            reverse('post_view', kwargs={'id': self.post.id})
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.context['user_score'], 3)


class PostViewTests(TestCase):

    def test_visitante_nao_consegue_comentar(self):
        autor = User.objects.create_user('autor', password='x12345678')
        post = criar_post(autor, 'Meu post')
        url = reverse('post_view', kwargs={'id': post.id})

        resposta = self.client.post(url, {'comment': 'Oi'})

        self.assertRedirects(
            resposta,
            f'/accounts/login/?next={url}',
            fetch_redirect_response=False
        )
        self.assertEqual(Comment.objects.count(), 0)


class HomeBuscaTests(TestCase):

    def setUp(self):
        self.ana = User.objects.create_user(
            'ana', password='x12345678', first_name='Ana', last_name='Souza'
        )
        self.bruno = User.objects.create_user(
            'bruno', password='x12345678', first_name='Bruno', last_name='Lima'
        )

        criar_post(self.ana, 'Introdução ao Django', dias_atras=3)
        criar_post(self.bruno, 'Aprendendo Python', dias_atras=2)
        criar_post(self.bruno, 'Django avançado', dias_atras=1)

        self.url = reverse('home')

    def titulos(self, **params):
        resposta = self.client.get(self.url, params)
        self.assertEqual(resposta.status_code, 200)
        return [post.title for post in resposta.context['posts']]

    def test_lista_os_mais_recentes_primeiro(self):
        self.assertEqual(
            self.titulos(),
            ['Django avançado', 'Aprendendo Python', 'Introdução ao Django']
        )

    def test_ordena_pelos_mais_antigos(self):
        self.assertEqual(
            self.titulos(ordem='antigos'),
            ['Introdução ao Django', 'Aprendendo Python', 'Django avançado']
        )

    def test_busca_pelo_titulo(self):
        self.assertEqual(
            self.titulos(q='django', campo='titulo'),
            ['Django avançado', 'Introdução ao Django']
        )

    def test_busca_pelo_autor(self):
        self.assertEqual(
            self.titulos(q='bruno', campo='autor'),
            ['Django avançado', 'Aprendendo Python']
        )

    def test_busca_pelo_nome_completo_do_autor(self):
        self.assertEqual(
            self.titulos(q='Ana Souza', campo='autor'),
            ['Introdução ao Django']
        )

    def test_campo_titulo_nao_procura_no_autor(self):
        self.assertEqual(self.titulos(q='bruno', campo='titulo'), [])

    def test_campo_todos_procura_em_titulo_e_autor(self):
        self.assertEqual(self.titulos(q='ana'), ['Introdução ao Django'])
        self.assertEqual(
            self.titulos(q='python'),
            ['Aprendendo Python']
        )

    def test_varias_palavras_precisam_aparecer_todas(self):
        self.assertEqual(
            self.titulos(q='bruno django'),
            ['Django avançado']
        )

    def test_busca_combinada_com_ordem(self):
        self.assertEqual(
            self.titulos(q='bruno', campo='autor', ordem='antigos'),
            ['Aprendendo Python', 'Django avançado']
        )

    def test_parametros_invalidos_usam_o_padrao(self):
        self.assertEqual(
            self.titulos(campo='xyz', ordem='abc'),
            ['Django avançado', 'Aprendendo Python', 'Introdução ao Django']
        )

    def test_posts_ocultos_nao_aparecem(self):
        criar_post(self.ana, 'Rascunho', is_active=False)
        criar_post(self.ana, 'Apagado', is_deleted=True)

        self.assertNotIn('Rascunho', self.titulos())
        self.assertNotIn('Apagado', self.titulos())

    def test_paginacao(self):
        for i in range(8):
            criar_post(self.ana, f'Extra {i}')

        # 11 posts no total, 6 por página
        pagina_1 = self.client.get(self.url)
        pagina_2 = self.client.get(self.url, {'page': 2})

        self.assertEqual(pagina_1.context['total'], 11)
        self.assertEqual(len(pagina_1.context['posts']), 6)
        self.assertEqual(len(pagina_2.context['posts']), 5)

    def test_pagina_inexistente_mostra_a_ultima(self):
        resposta = self.client.get(self.url, {'page': 999})

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.context['page_obj'].number, 1)

    def test_links_de_pagina_mantem_a_busca(self):
        for i in range(8):
            criar_post(self.ana, f'Extra {i}')

        resposta = self.client.get(self.url, {'q': 'extra', 'ordem': 'antigos'})

        self.assertContains(resposta, 'q=extra')
        self.assertContains(resposta, 'ordem=antigos')
        self.assertContains(resposta, 'page=2')
