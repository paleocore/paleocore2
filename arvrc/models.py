from django.contrib.gis.db import models


# Create your models here.
class CollectionCode(models.Model):
    code = models.CharField(max_length=255, null=True, blank=True)
    institution = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, null=True, blank=True)
    example = models.CharField(max_length=255, null=True, blank=True)
    example_taxon = models.CharField(max_length=255, null=True, blank=True)
    geography = models.CharField(max_length=255, null=True, blank=True)
    commentsFS = models.TextField(null=True, blank=True)
    commentsSP = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ("geography", "code")
