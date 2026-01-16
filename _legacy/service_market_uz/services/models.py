from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    """Service Category (e.g., Plumbing, Cleaning)."""
    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.ImageField(upload_to='categories/', blank=True, null=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children'
    )

    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self):
        return self.name
