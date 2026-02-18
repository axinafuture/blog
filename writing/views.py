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

    from .models import DEFAULT_AI_SYSTEM, DEFAULT_AI_PROMPT, DEFAULT_SUGGEST_SYSTEM, DEFAULT_SUGGEST_PROMPT
    from structure.models import ContactMessage
    all_posts = Post.objects.all()
    ai_summary = AISummary.objects.filter(id=1).first()
    contact_messages = ContactMessage.objects.all()[:20]
    unread_count = ContactMessage.objects.filter(is_read=False).count()

    context = {
        'posts': posts.distinct(),
        'categories': categories,
        'tags': tags,
        'current_category': category_id,
        'current_tag': tag_id,
        'current_status': status,
        'current_placement': placement,
        'total_count': all_posts.count(),
        'published_count': all_posts.filter(is_published=True).count(),
        'draft_count': all_posts.filter(is_published=False).count(),
        'ai_summary': ai_summary,
        'ai_system': ai_summary.system_message if ai_summary else DEFAULT_AI_SYSTEM,
        'ai_prompt': ai_summary.prompt_template if ai_summary else DEFAULT_AI_PROMPT,
        'suggest_system': ai_summary.suggest_system if ai_summary else DEFAULT_SUGGEST_SYSTEM,
        'suggest_prompt': ai_summary.suggest_prompt if ai_summary else DEFAULT_SUGGEST_PROMPT,
        'contact_messages': contact_messages,
        'unread_count': unread_count,
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
    """에디터 이미지 업로드 처리 (큰 이미지 자동 리사이즈)"""
    if request.method == 'POST' and request.FILES.get('file'):
        image = request.FILES['file']
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'editor', 'images')
        os.makedirs(upload_dir, exist_ok=True)

        from PIL import Image
        img = Image.open(image)
        max_width = 1600

        if img.width > max_width:
            ratio = max_width / img.width
            new_size = (max_width, int(img.height * ratio))
            img = img.resize(new_size, Image.LANCZOS)

        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # 파일명: 제목_순서.jpg
        title = request.POST.get('title', '').strip()
        safe_title = re.sub(r'[^\w가-힣-]', '', title.replace(' ', '-'))[:30] or 'untitled'
        existing = [f for f in os.listdir(upload_dir) if f.startswith(f"{safe_title}_")]
        order = len(existing) + 1
        filename = f"{safe_title}_{order}.jpg"
        filepath = os.path.join(upload_dir, filename)
        img.save(filepath, 'JPEG', quality=85)

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

    # 요청에서 프롬프트 받기
    try:
        body = json.loads(request.body)
        user_system = body.get('system_message', '').strip()
        user_prompt = body.get('prompt_template', '').strip()
    except (json.JSONDecodeError, AttributeError):
        user_system = ''
        user_prompt = ''

    from .models import DEFAULT_AI_SYSTEM, DEFAULT_AI_PROMPT
    system_message = user_system or DEFAULT_AI_SYSTEM
    prompt_template = user_prompt or DEFAULT_AI_PROMPT

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

{prompt_template}"""

    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model='gpt-4o',
            messages=[
                {'role': 'system', 'content': system_message},
                {'role': 'user', 'content': prompt},
            ],
            max_tokens=1000,
            temperature=0.7,
        )
        ai_content = response.choices[0].message.content

        summary, _ = AISummary.objects.update_or_create(
            id=1,
            defaults={
                'content': ai_content,
                'system_message': system_message,
                'prompt_template': prompt_template,
            },
        )

        return JsonResponse({
            'success': True,
            'content': ai_content,
            'updated_at': summary.updated_at.strftime('%Y.%m.%d %H:%M'),
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def save_suggest_prompt(request):
    """AI 제안 프롬프트 저장"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    try:
        body = json.loads(request.body)
        suggest_system = body.get('suggest_system', '').strip()
        suggest_prompt = body.get('suggest_prompt', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not suggest_system or not suggest_prompt:
        return JsonResponse({'error': '프롬프트를 입력하세요.'}, status=400)

    from .models import DEFAULT_SUGGEST_SYSTEM, DEFAULT_SUGGEST_PROMPT
    summary, _ = AISummary.objects.get_or_create(id=1)
    summary.suggest_system = suggest_system
    summary.suggest_prompt = suggest_prompt
    summary.save()

    return JsonResponse({'success': True})


@login_required
def contact_action(request, pk):
    """문의 메시지 읽음/삭제 처리"""
    from structure.models import ContactMessage
    msg = get_object_or_404(ContactMessage, pk=pk)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'read':
            msg.is_read = True
            msg.save()
        elif action == 'delete':
            msg.delete()
    return redirect('manage')


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

    from .models import AISummary, DEFAULT_SUGGEST_SYSTEM, DEFAULT_SUGGEST_PROMPT
    ai_config = AISummary.objects.first()
    system_msg = ai_config.suggest_system if ai_config else DEFAULT_SUGGEST_SYSTEM
    prompt_tpl = ai_config.suggest_prompt if ai_config else DEFAULT_SUGGEST_PROMPT
    prompt = prompt_tpl.replace('{text}', clean_text)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {'role': 'system', 'content': system_msg},
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
