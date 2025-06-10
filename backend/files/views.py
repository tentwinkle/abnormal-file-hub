from django.db.models import Sum, Min
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import File
from .serializers import FileSerializer
import hashlib

# Create your views here.

class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer

    def get_queryset(self):
        queryset = File.objects.all()
        params = self.request.query_params

        search = params.get('search')
        if search:
            queryset = queryset.filter(original_filename__icontains=search)

        file_type = params.get('file_type')
        if file_type:
            queryset = queryset.filter(file_type=file_type)

        size_min = params.get('size_min')
        if size_min is not None:
            queryset = queryset.filter(size__gte=int(size_min))

        size_max = params.get('size_max')
        if size_max is not None:
            queryset = queryset.filter(size__lte=int(size_max))

        date_from = params.get('date_from')
        if date_from:
            queryset = queryset.filter(uploaded_at__date__gte=date_from)

        date_to = params.get('date_to')
        if date_to:
            queryset = queryset.filter(uploaded_at__date__lte=date_to)

        return queryset

    def create(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        # Compute hash for deduplication
        file_bytes = file_obj.read()
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        file_obj.seek(0)

        # Check for existing file with same hash and size
        try:
            existing = File.objects.filter(file_hash=file_hash, size=file_obj.size).first()
        except File.DoesNotExist:
            existing = None

        if existing:
            # Create new record referencing existing file path
            new_record = File.objects.create(
                file=existing.file.name,
                original_filename=file_obj.name,
                file_type=file_obj.content_type,
                size=file_obj.size,
                file_hash=file_hash,
            )
            serializer = self.get_serializer(new_record)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        data = {
            'file': file_obj,
            'original_filename': file_obj.name,
            'file_type': file_obj.content_type,
            'size': file_obj.size,
            'file_hash': file_hash,
        }

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'])
    def savings(self, request):
        """Return total storage saved by deduplication."""
        total_size = File.objects.aggregate(total=Sum('size'))['total'] or 0
        unique_size = (
            File.objects.values('file_hash')
            .annotate(min_size=Min('size'))
            .aggregate(total=Sum('min_size'))['total']
            or 0
        )
        return Response({'storage_savings': total_size - unique_size})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()
