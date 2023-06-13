from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    text = models.TextField('текст')
    pub_date = models.DateTimeField('дата публикации', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='автор')
    group = models.ForeignKey('Group', on_delete=models.CASCADE,
                              blank=True, null=True,
                              related_name='posts',
                              verbose_name='группа')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text


class Group(models.Model):
    title = models.CharField('заголовок', max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField('описание')

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='comments')
    text = models.TextField('текст')
    created = models.DateTimeField('дата публикации', auto_now_add=True)

    def __str__(self):
        return self.text
