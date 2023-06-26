from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    title = models.CharField(verbose_name='Title', max_length=200,
                             blank=True, null=True)
    text = models.TextField(verbose_name='Text')
    pub_date = models.DateTimeField(verbose_name='Publication date',
                                    auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='Author')
    group = models.ForeignKey('Group', on_delete=models.CASCADE,
                              blank=True, null=True,
                              related_name='posts',
                              verbose_name='Group')
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text


class Group(models.Model):
    title = models.CharField(verbose_name='Title', max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name='Description')

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


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following')
