from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .models import Group, Post, User, Follow
from .forms import PostForm, CommentForm

POSTS_PER_PAGE = 10


def paginator(posts, request):
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


@cache_page(20)
def index(request):
    posts = Post.objects.all()
    page_obj = paginator(posts, request)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = paginator(posts, request)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    profile = get_object_or_404(User, username=username)
    posts = profile.posts.all()
    page_obj = paginator(posts, request)
    following = request.user.is_authenticated and Follow.objects.filter(
        author__username=username,
    ).exists()

    context = {
        'profile': profile,
        'page_obj': page_obj,
        'posts': posts,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    # комментарии берутся в самом шаблоне post.comments.all
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'form': form,
        'available_for_comment': True,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form = post.save()
        return redirect('posts:profile', username=request.user.username)

    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post.pk)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post = form.save(commit=False)
        form = post.save()
        return redirect('posts:post_detail', post_id=post_id)

    context = {
        'form': form,
        'post': post,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    # будут выведены посты авторов, на которых подписан текущий пользователь
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator(posts, request)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # подписка
    following_author = get_object_or_404(User, username=username)
    if request.user != following_author:
        Follow.objects.get_or_create(
            user=request.user,
            author=following_author,
        )
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    # отписка
    Follow.objects.filter(
        author__username=username,
    ).delete()
    return redirect('posts:follow_index')
