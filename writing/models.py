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


class AISummary(models.Model):
    content = models.TextField(verbose_name='AI 요약')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='생성일')

    class Meta:
        verbose_name = 'AI 요약'
        verbose_name_plural = 'AI 요약'

    def __str__(self):
        return f'AI 요약 ({self.updated_at.strftime("%Y.%m.%d %H:%M")})'
