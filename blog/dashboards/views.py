from django.shortcuts import get_object_or_404, redirect, render

from blogs.models import Blog, Category
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import AddUserForm, BlogPostForm, CategoryForm, EditUserForm
from django.template.defaultfilters import slugify
from django.contrib.auth.models import User
from django.db.models import Q

@login_required(login_url='login')
def dashboard(request):
    category_count = Category.objects.all().count()
    blogs_count = Blog.objects.all().count()
    user_count = User.objects.all().count()
       
    context = {
        'category_count': category_count,
        'blogs_count': blogs_count,
        'user_count': user_count,
    }
    return render(request, 'dashboard/dashboard.html', context)

# def categories(request):
#     return render(request, 'dashboard/categories.html')


def categories(request):
    keyword = request.GET.get('keyword')  # get search input
    
    categories = Category.objects.all()   # get all categories

    if keyword:
        categories = categories.filter(category_name__icontains=keyword)

    context = {
        'categories': categories
    }

    return render(request, 'dashboard/categories.html', context)

def add_category(request):

    # 🔐 Permission Check
    if not (
        request.user.is_superuser or 
        request.user.groups.filter(name__in=["Manager", "Editor"]).exists()
    ):
        return HttpResponse("You are not allowed to add category")

    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories')

    context = {
        'form': form,
    }

    return render(request, 'dashboard/add_category.html', context)


def edit_category(request, pk):

    # 🔐 Permission Check
    if not (
        request.user.is_superuser or 
        request.user.groups.filter(name__in=["Manager", "Editor"]).exists()
    ):
        return HttpResponse("You are not allowed to edit category")

    category = get_object_or_404(Category, pk=pk)

    form = CategoryForm(instance=category)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('categories')

    context = {
        'form': form,
        'category': category,
    }

    return render(request, 'dashboard/edit_category.html', context)


def delete_category(request, pk):

    # 🔐 Permission Check (ONLY Admin + Manager)
    if not (
        request.user.is_superuser or 
        request.user.groups.filter(name="Manager").exists()
    ):
        return HttpResponse("You are not allowed to delete category")

    category = get_object_or_404(Category, pk=pk)
    category.delete()

    return redirect('categories')



 

def posts(request):
    keyword = request.GET.get('keyword')  # get search input

    posts = Blog.objects.all()

    if keyword:
        posts = posts.filter(
            Q(title__icontains=keyword) |
            Q(category__category_name__icontains=keyword) |
            Q(author__username__icontains=keyword)
        )

    context = {
        'posts': posts,
    }

    return render(request, 'dashboard/posts.html', context)


def add_post(request):
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False) # temporarily saving the form
            post.author = request.user
            post.save()
            title = form.cleaned_data['title']
            post.slug = slugify(title) + '-'+str(post.id)
            post.save()
            return redirect('posts')
        else:
            print('form is invalid')
            print(form.errors)
    form = BlogPostForm()
    context = {
        'form': form,
    }
    return render(request, 'dashboard/add_post.html', context)


def edit_post(request, pk):
    post = get_object_or_404(Blog, pk=pk)

    # 🔐 SECURITY CHECK
    if not (
        post.author == request.user or 
        request.user.is_superuser or 
        request.user.groups.filter(name__in=["Manager", "Editor"]).exists()
    ):
        return HttpResponse("You are not allowed to edit this post")

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)

        if form.is_valid():
            post = form.save(commit=False)
            post.slug = slugify(post.title) + '-' + str(post.id)
            post.save()
            return redirect('posts')

    else:
        form = BlogPostForm(instance=post)

    return render(request, 'dashboard/edit_post.html', {
        'form': form,
        'post': post
    })


def delete_post(request, pk):
    post = get_object_or_404(Blog, pk=pk)

    # 🔐 SECURITY CHECK
    if not (
        post.author == request.user or 
        request.user.is_superuser or 
        request.user.groups.filter(name__in=["Manager", "Editor"]).exists()
    ):
        return HttpResponse("You are not allowed to delete this post")

    post.delete()
    return redirect('posts')


def users(request):
    users = User.objects.all()
    context = {
        'users': users,
    }
    return render(request, 'dashboard/users.html', context)


def add_user(request):
    if request.method == 'POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users')
        else:
            print(form.errors)
    form = AddUserForm()
    context = {
        'form': form,
    }
    return render(request, 'dashboard/add_user.html', context)


def edit_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('users')
    form = EditUserForm(instance=user)
    context = {
        'form': form,
    }
    return render(request, 'dashboard/edit_user.html', context)


def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    return redirect('users')