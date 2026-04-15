# models.py
from django.db import models
from django.utils.html import mark_safe

class Technology(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Technologies"

class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    github_link = models.URLField(blank=True, null=True)
    demo_link = models.URLField(blank=True, null=True)
    download_link = models.URLField(blank=True, null=True)
    technologies = models.ManyToManyField(Technology, related_name='projects', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']

class ProjectImage(models.Model):
    project = models.ForeignKey(Project, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='projects/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.project.title} - Image {self.order}"
    
    class Meta:
        ordering = ['order']

class Feature(models.Model):
    project = models.ForeignKey(Project, related_name='features', on_delete=models.CASCADE)
    feature = models.CharField(max_length=200)
    
    def __str__(self):
        return self.feature

# Add this new model for contact messages
class ContactMessage(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Contact Messages"