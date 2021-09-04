from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from .models import Group, Post, User, Follow
from .forms import PostForm, CommentForm

POSTS_PER_PAGE = 10


def paginator(posts, request):
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


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

    # передать, какую кнопку показать
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=profile,
        )

    # не показывать кнопку "подписаться/отписаться" на себя
    show = True
    if profile == request.user:
        show = False

    # подписан
    count_follower = profile.follower.all().count()
    # подписчиков
    count_following = profile.following.all().count()

    context = {
        'profile': profile,
        'page_obj': page_obj,
        'posts': posts,
        'following': following,
        'show': show,
        'count_following': count_following,
        'count_follower': count_follower,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    comments = post.comments.all()
    context = {
        'post': post,
        'comments': comments,
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
    following_author = User.objects.get(username=username)
    repeat = Follow.objects.filter(
        user=request.user,
        author=following_author,
    )
    if (request.user != following_author) and (not repeat):
        Follow.objects.create(
            user=request.user,
            author=following_author,
        )
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    # отписка
    following_author = User.objects.get(username=username)
    Follow.objects.filter(
        user=request.user,
        author=following_author,
    ).delete()
    return redirect('posts:follow_index')
