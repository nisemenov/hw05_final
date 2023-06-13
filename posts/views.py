from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from .models import Post, Group, User, Comment
from .forms import PostForm, CommentForm

import datetime as dt


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html',
                  {'page': page, 'paginator': paginator})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html',
                  {'group': group, 'page': page, 'paginator': paginator})


@ login_required()
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'new_post.html', {'form': form})


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    posts_list = profile.posts.all()
    paginator = Paginator(posts_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'profile.html', {'profile': profile,
                                            'page': page,
                                            'paginator': paginator})


def post_view(request, username, post_id):
    profile = get_object_or_404(User, username=username)
    post = profile.posts.get(id=post_id)
    comments = Comment.objects.filter(post=post_id)
    form = CommentForm()
    return render(request, 'post.html', {'profile': profile,
                                         'post': post,
                                         'comments': comments,
                                         'form': form})


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
        post.pub_date = dt.datetime.now() + dt.timedelta(hours=2)
        post.save()
        return redirect('post', username, post_id)
    return render(request, 'post_edit.html', {'form': form,
                                              'profile': profile,
                                              'post': post})


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
