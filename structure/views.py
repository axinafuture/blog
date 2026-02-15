from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from writing.models import Post, Category, AISummary


def main(request):
    main_posts = Post.objects.filter(
        is_published=True, placement='main'
    ).select_related('category')[:3]
    ai_summary = AISummary.objects.filter(id=1).first()
    return render(request, 'main.html', {
        'main_posts': main_posts,
        'ai_summary': ai_summary,
    })


def essay(request):
    posts = Post.objects.filter(is_published=True).select_related('category')
    categories = Category.objects.all()

    category_id = request.GET.get('category')
    if category_id:
        posts = posts.filter(category_id=category_id)

    query = request.GET.get('q', '').strip()
    if query:
        posts = posts.filter(Q(title__icontains=query) | Q(content__icontains=query))

    paginator = Paginator(posts, 20)
    page = request.GET.get('page')
    posts = paginator.get_page(page)

    context = {
        'posts': posts,
        'categories': categories,
        'current_category': int(category_id) if category_id else None,
        'query': query,
    }
    return render(request, 'essay.html', context)


def essay_detail(request, pk):
    post = get_object_or_404(Post, pk=pk, is_published=True)
    categories = Category.objects.all()
    context = {
        'post': post,
        'categories': categories,
    }
    return render(request, 'essay_detail.html', context)
