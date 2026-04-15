from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from datetime import date

class PortfolioSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    
    def items(self):
        # These are the URL names from your urls.py
        return ['index', 'about', 'projects', 'skills', 'contact']
    
    def location(self, item):
        # This converts URL names to actual paths
        return reverse(item)
    
    def lastmod(self, item):
        # Returns today's date (you can customize this later)
        return date.today()
    
    def priority(self, item):
        # Custom priority for each page
        priorities = {
            'index': 1.0,      # Homepage - highest priority
            'about': 0.8,
            'projects': 0.9,   # Projects - high priority
            'skills': 0.7,
            'contact': 0.6,
        }
        return priorities.get(item, 0.5)
    
    def changefreq(self, item):
        # How often each page changes
        frequencies = {
            'index': 'weekly',
            'about': 'monthly',
            'projects': 'weekly',   # You'll add projects often
            'skills': 'monthly',
            'contact': 'yearly',
        }
        return frequencies.get(item, 'monthly')