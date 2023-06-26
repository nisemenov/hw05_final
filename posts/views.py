from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
)

from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm

import datetime as dt


class PostListView(ListView):
    model = Post
    template_name = 'index.html'
    paginate_by = 10


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html',
                  {'group': group, 'page': page, 'paginator': paginator})


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'new_post.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        messages.add_message(
            self.request, messages.SUCCESS, f'Post "{post.title}" was added',
            extra_tags='success'
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('index')

    def form_invalid(self, form):
        messages.add_message(
            self.request,
            messages.ERROR,
            'Error occurred while creating a post',
            extra_tags='error'
        )
        return super().form_invalid(form)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    following = False
    if request.user.is_authenticated:
        authors_list = [i[0] for i in
                        request.user.follower.all().values_list('author')]
        if profile.pk in authors_list:
            following = True
    posts_list = profile.posts.all()
    paginator = Paginator(posts_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {'profile': profile,
                                            'page': page,
                                            'paginator': paginator,
                                            'following': following})


def post_view(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    following = False
    if request.user.is_authenticated:
        authors_list = [i[0] for i in
                    request.user.follower.all().values_list('author')]
        if profile.pk in authors_list:
            following = True
    post = profile.posts.get(id=post_id)
    comments = Comment.objects.filter(post=post_id)
    form = CommentForm()
    return render(request, 'post.html', {'profile': profile,
                                         'post': post,
                                         'comments': comments,
                                         'form': form,
                                         'following': following})


@login_required()
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
        return redirect('post', username=username, post_id=post_id)
    return redirect('post', username=username, post_id=post_id)


@ login_required()
def post_edit(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = profile.posts.get(id=post_id)
    if request.user != profile:
        return redirect('post', username, post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        post.pub_date = dt.datetime.now()
        post.save()
        messages.add_message(
            request, messages.SUCCESS, f'Post "{post.title}" was changed!',
            extra_tags='success'
        )
        return redirect('post', username, post_id)
    return render(request, 'post_edit.html', {'form': form,
                                              'profile': profile,
                                              'post': post})


@login_required
def follow_index(request):
    # authors_list = request.user.follower.all().values('author')
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, "follow.html", {'page': page,
                                           'paginator': paginator})


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    authors_list = [i[0] for i in
                    request.user.follower.all().values_list('author')]
    if request.user != author and author.pk not in authors_list:
        Follow.objects.create(user=request.user, author=author)
        return redirect('follow_index')
    return redirect('follow_index')


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.get(user=request.user, author=author).delete()
    return redirect('follow_index')


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(
        request,
        'misc/404.html',
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
