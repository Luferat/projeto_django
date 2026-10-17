
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from projectus.models import Post


class Command(BaseCommand):
    help = 'Popula a tabela Post com dados fictícios'

    def handle(self, *args, **options):
        User = get_user_model()
        users = list(User.objects.all()[:5])

        if not users:
            self.stdout.write(
                self.style.ERROR(
                    'Crie pelo menos um usuário antes de popular os posts.'
                )
            )
            return

        dados = [
            {
                'title': 'Introdução ao Django',
                'summary': 'Conheça o framework web Python.',
                'thumbnail': 'https://picsum.photos/seed/django/800/450',
                'textbody': 'Django é um framework web poderoso para Python.',
            },
            {
                'title': 'Aprendendo Python',
                'summary': 'Os primeiros passos com Python.',
                'thumbnail': 'https://picsum.photos/seed/python/800/450',
                'textbody': 'Python é uma linguagem simples e versátil.',
            },
            {
                'title': 'O que é um ORM?',
                'summary': 'Entenda como trabalhar com bancos de dados.',
                'thumbnail': 'https://picsum.photos/seed/orm/800/450',
                'textbody': 'Um ORM permite manipular dados usando objetos.',
            },
            {
                'title': 'Criando APIs REST',
                'summary': 'Aprenda os conceitos básicos de uma API.',
                'thumbnail': 'https://picsum.photos/seed/api/800/450',
                'textbody': 'APIs REST permitem a comunicação entre aplicações.',
            },
            {
                'title': 'Templates no Django',
                'summary': 'Organize o HTML da sua aplicação.',
                'thumbnail': 'https://picsum.photos/seed/templates/800/450',
                'textbody': 'Os templates separam a apresentação da lógica.',
            },
        ]

        posts = [
            Post(
                user=users[i % len(users)],
                **dados[i],
            )
            for i in range(len(dados))
        ]

        Post.objects.bulk_create(posts)

        self.stdout.write(
            self.style.SUCCESS(
                f'{len(posts)} posts criados com sucesso!'
            )
        )
