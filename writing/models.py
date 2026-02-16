from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='카테고리명')

    class Meta:
        verbose_name = '카테고리'
        verbose_name_plural = '카테고리'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='태그명')

    class Meta:
        verbose_name = '태그'
        verbose_name_plural = '태그'

    def __str__(self):
        return self.name


PLACEMENT_CHOICES = [
    ('none', '배치 안함'),
    ('main', '메인 페이지'),
]


class Post(models.Model):
    title = models.CharField(max_length=200, verbose_name='제목')
    content = models.TextField(verbose_name='내용')
    thumbnail = models.ImageField(upload_to='thumbnails/%Y/%m/', blank=True, null=True, verbose_name='썸네일')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='카테고리')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='태그')
    placement = models.CharField(max_length=20, choices=PLACEMENT_CHOICES, default='none', verbose_name='배치')
    is_published = models.BooleanField(default=False, verbose_name='공개 여부')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='작성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        ordering = ['-created_at']
        verbose_name = '게시글'
        verbose_name_plural = '게시글'

    def __str__(self):
        return self.title


DEFAULT_AI_SYSTEM = '당신은 블로그의 글을 읽고, 작가의 최근 생각을 조용히 정리해주는 편집자입니다.'

DEFAULT_AI_PROMPT = """위 글들을 바탕으로, 이 블로그 작가가 최근 어떤 생각을 하고 있는지 정리하는 짧은 글을 작성해주세요.

- 글을 추천하거나 가이드하지 말 것
- 카테고리 설명이나 목록 나열 금지
- 글쓴이의 최근 관심사, 고민, 시선의 흐름을 하나의 맥락으로 묶어 서술
- 담백하고 사적인 에세이 톤
- 분석적이지 않고, 정리된 사유처럼 작성
- 존대말의 종결형식을 사용
- HTML 형식 (h3, p 태그만 사용)
- 전체 길이 300자 내외"""


class AISummary(models.Model):
    content = models.TextField(verbose_name='AI 요약', blank=True, default='')
    system_message = models.TextField(verbose_name='시스템 메시지', default=DEFAULT_AI_SYSTEM)
    prompt_template = models.TextField(verbose_name='프롬프트', default=DEFAULT_AI_PROMPT)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='생성일')

    class Meta:
        verbose_name = 'AI 요약'
        verbose_name_plural = 'AI 요약'

    def __str__(self):
        return f'AI 요약 ({self.updated_at.strftime("%Y.%m.%d %H:%M")})'
