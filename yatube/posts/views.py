from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import POSTS_LIMIT
from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from .utils import paginator


def index(request):
    title = 'Последние обновления на сайте.'
    posts_list = Post.objects.select_related().all()
    page_obj = paginator(request, posts_list, POSTS_LIMIT)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.select_related('group').filter(group=group)
    page_obj = paginator(request, posts, POSTS_LIMIT)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    a_posts = Post.objects.select_related('author').filter(author=author)
    a_posts_count = a_posts.count()
    page_obj = paginator(request, a_posts, POSTS_LIMIT)
    following = None
    self_sub = False
    if request.user.is_authenticated:
        if request.user == author:
            self_sub = True
        following = Follow.objects.filter(
            user=request.user, author=author).exists
    context = {
        'author': author,
        'a_posts_count': a_posts_count,
        'page_obj': page_obj,
        'following': following,
        'self_sub': self_sub,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    a_posts = Post.objects.select_related('author').filter(author=post.author)
    a_posts_count = a_posts.count()
    comments = Comment.objects.filter(post=post.pk)
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'a_posts_count': a_posts_count,
        'comments': comments,
        'form': form,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    title = 'Новый пост'
    button = 'Добавить'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:profile', post.author.username)
    context = {
        'form': form,
        'title': title,
        'button': button,
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    is_edit = True
    title = 'Редактировать пост'
    button = 'Сохранить'
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': is_edit,
        'title': title,
        'button': button,
    }
    return render(request, 'posts/post_create.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    title = 'Последние посты авторов, на которых вы подписаны'
    posts_list = Post.objects.select_related('author').filter(
        author__following__user=request.user)
    page_obj = paginator(request, posts_list, POSTS_LIMIT)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = get_object_or_404(User, username=username)
    if request.user == user:
        return redirect('posts:profile', username)
    Follow.objects.get_or_create(user=request.user, author=user)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    user = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=user).delete()
    return redirect('posts:profile', username)
