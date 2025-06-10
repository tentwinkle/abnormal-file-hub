from django.db import models
import uuid
import os

def file_upload_path(instance, filename):
    """Generate file path for new file upload"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('uploads', filename)

class File(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to=file_upload_path)
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)
    size = models.BigIntegerField()
    file_hash = models.CharField(max_length=64, db_index=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['original_filename']),
            models.Index(fields=['file_type']),
            models.Index(fields=['size']),
            models.Index(fields=['uploaded_at']),
            models.Index(fields=['file_hash']),
        ]
    
    def __str__(self):
        return self.original_filename

    def delete(self, using=None, keep_parents=False):
        """Remove DB record and delete file from disk if no other records reference it."""
        file_path = self.file.name
        super().delete(using=using, keep_parents=keep_parents)
        if not File.objects.filter(file=file_path).exists():
            storage = self.file.storage
            if storage.exists(file_path):
                storage.delete(file_path)
