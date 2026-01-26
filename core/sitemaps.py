from django.contrib import sitemaps
from django.urls import reverse

class StaticViewSitemap(sitemaps.Sitemap):
    """Main static pages with highest priority"""
    priority = 1.0
    changefreq = 'weekly'

    def items(self):
        return ['home', 'services', 'about', 'contact']

    def location(self, item):
        return reverse(item)


class ToolsSitemap(sitemaps.Sitemap):
    """PDF Tools pages - important for SEO"""
    priority = 0.9
    changefreq = 'weekly'

    def items(self):
        return [
            'tools_list',
            'pdf_to_word_tool',
            'word_to_pdf_tool',
            'merge_pdf_tool',
            'split_pdf_tool',
            'compress_pdf_tool',
            'pdf_to_ppt_tool',
            'pdf_to_excel_tool',
            'excel_to_pdf_tool',
            'ppt_to_pdf_tool',
            'pdf_to_jpg_tool',
            'jpg_to_pdf_tool',
            'sign_pdf_tool',
            'html_to_pdf_tool',
            'rotate_pdf_tool',
            'add_watermark_tool',
            'protect_pdf_tool',
            'unlock_pdf_tool',
            'add_page_numbers_tool',
            'remove_pages_tool',
            'extract_pages_tool',
            'whiteboard_tool',
        ]

    def location(self, item):
        return reverse(item)


class SecondaryPagesSitemap(sitemaps.Sitemap):
    """Secondary pages with lower priority"""
    priority = 0.6
    changefreq = 'monthly'

    def items(self):
        return ['signup', 'login', 'faqs', 'case_studies', 'terms', 'privacy']

    def location(self, item):
        return reverse(item)
