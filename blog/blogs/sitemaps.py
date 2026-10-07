from django.contrib.sitemaps import Sitemap
from .models import Blog


class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Blog.objects.filter(status="Published").order_by("-updated_at")

    def location(self, obj):
        return f"/blogs/{obj.slug}/"