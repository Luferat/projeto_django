from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, Count
from django.conf import settings


class PostQuerySet(models.QuerySet):

    def visible(self):
        """Posts que podem ser exibidos no site."""
        return self.filter(is_active=True, is_deleted=False)

    def with_ratings(self):
        """Adiciona `avg_rating` (média) e `votes_count` (nº de votos)."""
        return self.annotate(
            avg_rating=Avg('ratings__score'),
            votes_count=Count('ratings', distinct=True),
        )


class Post(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )

    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    thumbnail = models.URLField()
    textbody = models.TextField()
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    objects = PostQuerySet.as_manager()

    @property
    def author_name(self):
        """Nome para exibir do autor: nome completo, nome ou usuário."""
        user = self.user

        if user.first_name and user.last_name:
            return f'{user.first_name} {user.last_name}'
        if user.first_name:
            return user.first_name
        return user.username

    def __str__(self):
        return self.title


class Comment(models.Model):

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField()
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.comment


class Rating(models.Model):
    """Voto (de 1 a 5 estrelas) de um usuário em um post.

    Cada usuário pode votar uma única vez por post; votar de novo
    apenas altera a nota anterior.
    """

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='ratings'
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ratings'
    )

    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['post', 'user'],
                name='unique_rating_per_user_and_post'
            ),
        ]

    def __str__(self):
        return f'{self.user} -> {self.post} ({self.score}★)'
