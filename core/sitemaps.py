from django.contrib import sitemaps
from django.urls import reverse

class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        return ['home', 'services', 'about', 'contact', 'signup', 'login']

    def location(self, item):
        return reverse(item)
