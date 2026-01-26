from django.contrib import sitemaps
from django.urls import reverse
from .models import BlogPost

class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.9
    changefreq = 'daily'

    def items(self):
        return ['home', 'about', 'services', 'contact', 'tools_list', 'login', 'signup']

    def location(self, item):
        return reverse(item)

class ToolsSitemap(sitemaps.Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'merge_pdf_tool', 'split_pdf_tool', 'compress_pdf_tool',
            'pdf_to_word_tool', 'pdf_to_excel_tool', 'pdf_to_ppt_tool',
            'word_to_pdf_tool', 'excel_to_pdf_tool', 'ppt_to_pdf_tool',
            'pdf_to_jpg_tool', 'jpg_to_pdf_tool', 'sign_pdf_tool',
            'html_to_pdf_tool', 'rotate_pdf_tool', 'add_watermark_tool',
            'protect_pdf_tool', 'unlock_pdf_tool', 'add_page_numbers_tool',
            'remove_pages_tool', 'extract_pages_tool', 'whiteboard_tool',
        ]

    def location(self, item):
        return reverse(item)

class BlogSitemap(sitemaps.Sitemap):
    priority = 0.7
    changefreq = 'weekly'

    def items(self):
        try:
            return BlogPost.objects.filter(is_published=True)
        except:
            return []

    def lastmod(self, obj):
        return obj.updated_at

class SecondaryPagesSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'monthly'

    def items(self):
        return ['faqs', 'case_studies', 'terms', 'privacy']

    def location(self, item):
        return reverse(item)
