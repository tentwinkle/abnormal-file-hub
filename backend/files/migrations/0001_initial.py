from django.db import migrations, models
import uuid
import files.models

class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('file', models.FileField(upload_to=files.models.file_upload_path)),
                ('original_filename', models.CharField(max_length=255)),
                ('file_type', models.CharField(max_length=100)),
                ('size', models.BigIntegerField()),
                ('file_hash', models.CharField(max_length=64, db_index=True)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-uploaded_at'],
                'indexes': [
                    models.Index(fields=['original_filename']),
                    models.Index(fields=['file_type']),
                    models.Index(fields=['size']),
                    models.Index(fields=['uploaded_at']),
                    models.Index(fields=['file_hash']),
                ],
            },
        ),
    ]
