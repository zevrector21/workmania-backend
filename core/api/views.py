from django.conf import settings
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework_extensions.mixins import NestedViewSetMixin
from datetime import datetime
from core.models import *
from .serializers import *
from .utilities import get_ip_location


class ResourceViewSet(viewsets.ModelViewSet):
    serializer_class = ResourceSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = self.request.user.files.all()
        return queryset

    def create(self, request, *args, **kwargs):
        try:
            file_obj = request.FILES.get('file')
            category = request.POST['category']

            # # S3 upload
            # s3 = boto3.client(
            #     's3',
            #     aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            #     aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            #     region_name=getattr(settings, 'AWS_S3_REGION_NAME', None)
            # )
            # # Generate a unique filename
            # filename = f"{category}/{uuid.uuid4().hex}_{file_obj.name}"
            # s3.upload_fileobj(
            #     file_obj,
            #     settings.AWS_STORAGE_BUCKET_NAME,
            #     filename,
            #     ExtraArgs={'ACL': 'public-read'}
            # )
            # s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{filename}"

            # resource = Resource.objects.create(
            #     name=file_obj.name,
            #     category=category,
            #     file=s3_url,  # Save the S3 URL
            #     size=file_obj.size  # Save the file size
            # )

            resource = Resource.objects.create(
                name=file_obj.name,
                category=category,
                file="temporary_url",  # Save the S3 URL
                size="100 KB"  # Save the file size
            )

            serializer = ResourceSerializer(resource, context={'request': request})
            result = serializer.data

            return Response(result)
        except Exception as ex:
            return Response(str(ex), status=400)
