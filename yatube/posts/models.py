from django.contrib.auth import get_user_model
from django.db import models

from core.models import PubDateModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200, help_text="200 символов максимум",
    )
    slug = models.SlugField(unique=True,)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(PubDateModel):
    text = models.TextField()
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts",
    )
    group = models.ForeignKey(
        Group, models.SET_NULL, blank=True, null=True, related_name="posts",
    )
    image = models.ImageField("Картинка", upload_to="posts/", blank=True)


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments",
    )
    text = models.TextField()
    created = models.DateTimeField("date published", auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.text


class Follow(models.Model):
    # ссылка на объект пользователя, который подписывается
    user = models.ForeignKey(
        User, related_name="follower", on_delete=models.CASCADE,
    )
    # ссылка на объект пользователя, на которого подписываются
    author = models.ForeignKey(
        User, related_name="following", blank=True, null=True,
        on_delete=models.CASCADE,
    )
