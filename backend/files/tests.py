import os
import hashlib
import tempfile
from django.test import TestCase, override_settings
from django.core.files.base import ContentFile
from .models import File


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class FileModelDeleteTests(TestCase):
    def setUp(self):
        self.content = ContentFile(b"data", name="test.txt")
        self.hash = hashlib.sha256(b"data").hexdigest()

    def _create_file(self):
        return File.objects.create(
            file=self.content,
            original_filename=self.content.name,
            file_type="text/plain",
            size=self.content.size,
            file_hash=self.hash,
        )

    def test_physical_file_removed_only_when_last_reference_deleted(self):
        file1 = self._create_file()
        file_path = file1.file.path
        file2 = File.objects.create(
            file=file1.file.name,
            original_filename="copy.txt",
            file_type="text/plain",
            size=file1.size,
            file_hash=file1.file_hash,
        )

        self.assertTrue(os.path.exists(file_path))
        file1.delete()
        # file should still exist because file2 references it
        self.assertTrue(os.path.exists(file_path))
        file2.delete()
        # physical file removed after last reference deleted
        self.assertFalse(os.path.exists(file_path))


