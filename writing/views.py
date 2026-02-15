from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Post, Category, Tag, AISummary
import os
import re
import json
import uuid
from django.conf import settings


@login_required
def write(request, pk=None):
    """글 작성 / 수정 페이지"""
    post = get_object_or_404(Post, pk=pk) if pk else None
    categories = Category.objects.all()
    tags = Tag.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title', '')
        content = request.POST.get('content', '')
        is_published = request.POST.get('is_published') == 'on'
        thumbnail = request.FILES.get('thumbnail')
        category_id = request.POST.get('category')
        tag_ids = request.POST.getlist('tags')
        placement = request.POST.get('placement', 'none')

        if post:
            post.title = title
            post.content = content
            post.is_published = is_published
            post.placement = placement
            if category_id:
                post.category_id = int(category_id)
            else:
                post.category = None
            if thumbnail:
                post.thumbnail = thumbnail
        else:
            post = Post(
                title=title,
                content=content,
                is_published=is_published,
                thumbnail=thumbnail,
                placement=placement,
            )
            if category_id:
                post.category_id = int(category_id)
        post.save()
        post.tags.set(tag_ids)
        return redirect('manage')

    context = {
        'post': post,
        'categories': categories,
        'tags': tags,
    }
    return render(request, 'writing/write.html', context)


@login_required
def manage(request):
    """글 관리 페이지"""
    posts = Post.objects.select_related('category').prefetch_related('tags').all()
    categories = Category.objects.all()
    tags = Tag.objects.all()

    # 필터링
    category_id = request.GET.get('category')
    tag_id = request.GET.get('tag')
    status = request.GET.get('status')
    placement = request.GET.get('placement')

    if category_id:
        posts = posts.filter(category_id=category_id)
    if tag_id:
        posts = posts.filter(tags__id=tag_id)
    if status == 'published':
        posts = posts.filter(is_published=True)
    elif status == 'draft':
        posts = posts.filter(is_published=False)
    if placement:
        posts = posts.filter(placement=placement)

    context = {
        'posts': posts.distinct(),
        'categories': categories,
        'tags': tags,
        'current_category': category_id,
        'current_tag': tag_id,
        'current_status': status,
        'current_placement': placement,
    }
    return render(request, 'writing/manage.html', context)


@login_required
def post_update(request, pk):
    """글 속성 인라인 수정 (AJAX)"""
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        field = request.POST.get('field')

        if field == 'is_published':
            post.is_published = not post.is_published
            post.save()
            return JsonResponse({'value': post.is_published})

        elif field == 'placement':
            post.placement = request.POST.get('value', 'none')
            post.save()
            return JsonResponse({'value': post.placement})

        elif field == 'category':
            cat_id = request.POST.get('value')
            if cat_id:
                post.category_id = int(cat_id)
            else:
                post.category = None
            post.save()
            return JsonResponse({'value': str(post.category) if post.category else ''})

        elif field == 'tags':
            tag_ids = request.POST.getlist('value')
            post.tags.set(tag_ids)
            return JsonResponse({'value': list(post.tags.values_list('name', flat=True))})

    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def category_manage(request):
    """카테고리 추가/삭제"""
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            name = request.POST.get('name', '').strip()
            if name:
                Category.objects.get_or_create(name=name)
        elif action == 'delete':
            cat_id = request.POST.get('id')
            Category.objects.filter(id=cat_id).delete()
    return redirect('manage')


@login_required
def tag_manage(request):
    """태그 추가/삭제"""
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            name = request.POST.get('name', '').strip()
            if name:
                Tag.objects.get_or_create(name=name)
        elif action == 'delete':
            tag_id = request.POST.get('id')
            Tag.objects.filter(id=tag_id).delete()
    return redirect('manage')


@login_required
def delete(request, pk):
    """글 삭제"""
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        post.delete()
    return redirect('manage')


@login_required
@csrf_exempt
def image_upload(request):
    """에디터 이미지 업로드 처리"""
    if request.method == 'POST' and request.FILES.get('file'):
        image = request.FILES['file']
        ext = os.path.splitext(image.name)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'editor', 'images')
        os.makedirs(upload_dir, exist_ok=True)
        filepath = os.path.join(upload_dir, filename)

        with open(filepath, 'wb+') as f:
            for chunk in image.chunks():
                f.write(chunk)

        url = f"{settings.MEDIA_URL}editor/images/{filename}"
        return JsonResponse({'success': 1, 'file': {'url': url}})

    return JsonResponse({'success': 0}, status=400)


def _extract_text(content_json):
    """Editor.js JSON에서 텍스트 추출"""
    try:
        data = json.loads(content_json) if isinstance(content_json, str) else content_json
    except (json.JSONDecodeError, TypeError):
        return content_json
    texts = []
    for block in data.get('blocks', []):
        d = block.get('data', {})
        bt = block.get('type')
        if bt in ('paragraph', 'header', 'quote'):
            texts.append(re.sub(r'<[^>]+>', '', d.get('text', '')))
        elif bt == 'list':
            for item in d.get('items', []):
                texts.append(re.sub(r'<[^>]+>', '', item))
        elif bt == 'checklist':
            for item in d.get('items', []):
                texts.append(re.sub(r'<[^>]+>', '', item.get('text', '')))
    return ' '.join(texts)


@login_required
def generate_ai_summary(request):
    """OpenAI API로 공개된 글 분석 및 요약 생성"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    posts = Post.objects.filter(is_published=True).select_related('category')
    if not posts.exists():
        return JsonResponse({'error': '공개된 글이 없습니다.'}, status=400)

    post_summaries = []
    for post in posts[:20]:
        text = _extract_text(post.content)[:300]
        category = post.category.name if post.category else '미분류'
        post_summaries.append(f"- [{category}] {post.title}: {text}")

    posts_text = '\n'.join(post_summaries)

    prompt = f"""다음은 블로그에 공개된 글 목록입니다. 각 글의 카테고리, 제목, 내용 요약이 포함되어 있습니다.

{posts_text}

위 글들을 바탕으로, 이 블로그 작가가 최근 어떤 생각을 하고 있는지 정리하는 짧은 글을 작성해주세요.

- 글을 추천하거나 가이드하지 말 것
- 카테고리 설명이나 목록 나열 금지
- 글쓴이의 최근 관심사, 고민, 시선의 흐름을 하나의 맥락으로 묶어 서술
- 담백하고 사적인 에세이 톤
- 분석적이지 않고, 정리된 사유처럼 작성
- 존대말의 종결형식을 사용
- HTML 형식 (h3, p 태그만 사용)
- 전체 길이 300자 내외"""

    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {'role': 'system', 'content': '당신은 블로그의 글을 읽고, 작가의 최근 생각을 조용히 정리해주는 편집자입니다.'},
                {'role': 'user', 'content': prompt},
            ],
            max_tokens=1000,
            temperature=0.7,
        )
        ai_content = response.choices[0].message.content

        summary, _ = AISummary.objects.update_or_create(
            id=1,
            defaults={'content': ai_content},
        )

        return JsonResponse({
            'success': True,
            'content': ai_content,
            'updated_at': summary.updated_at.strftime('%Y.%m.%d %H:%M'),
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def ai_suggest(request):
    """단락 텍스트에 대한 AI 작문 개선 제안"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        body = json.loads(request.body)
        text = body.get('text', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not text or len(text) < 20:
        return JsonResponse({'error': 'Text too short'}, status=400)

    clean_text = re.sub(r'<[^>]+>', '', text)

    prompt = f"""다음 문장을 더 자연스럽고 명확하게 다듬어주세요.

원문:
{clean_text}

규칙:
- 원문의 의미와 톤을 유지할 것
- 문법, 맞춤법, 어색한 표현만 교정
- 이미 충분히 좋은 문장이면 원문을 그대로 반환
- 교정된 문장만 반환 (설명 없이)
- HTML 태그 없이 순수 텍스트만 반환"""

    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': '당신은 글을 다듬어주는 편집자입니다. 교정된 문장만 반환합니다.'},
                {'role': 'user', 'content': prompt},
            ],
            max_tokens=500,
            temperature=0.3,
        )
        suggestion = response.choices[0].message.content.strip()

        if suggestion == clean_text:
            return JsonResponse({'unchanged': True})

        return JsonResponse({
            'suggestion': suggestion,
            'original': clean_text,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
