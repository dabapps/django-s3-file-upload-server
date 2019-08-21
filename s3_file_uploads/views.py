from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, views
from rest_framework.response import Response
from django.urls import reverse
from s3_file_uploads.models import UploadedFile
from s3_file_uploads.serializers import UploadedFileSerializer, AccessControlListSerializer


class UploadedFileCreateView(generics.CreateAPIView):
    serializer_class = UploadedFileSerializer

    def get_queryset(self):
        return UploadedFile.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        acl_serialiser = AccessControlListSerializer(data=request.data)
        acl_serialiser.is_valid(raise_exception=True)
        file_serializer = self.get_serializer(
            data={**request.data, 'user': request.user.id}
        )
        file_serializer.is_valid(raise_exception=True)
        self.perform_create(file_serializer)
        headers = self.get_success_headers(file_serializer.data)
        uploaded_file = file_serializer.instance
        uploaded_file_data = UploadedFileSerializer(instance=uploaded_file).data
        uploaded_file_data['upload_form'] = uploaded_file.get_upload_form(
            acl_type=acl_serialiser.validated_data['acl']
        )
        uploaded_file_data['complete_url'] = request.build_absolute_uri(
            reverse('s3_file_uploads:upload-file-complete', args=(str(uploaded_file.id),))
        )
        return Response(uploaded_file_data, status=status.HTTP_201_CREATED, headers=headers)


class UploadedFileUploadCompleteView(views.APIView):
    def post(self, request, file_id):
        uploaded_file = get_object_or_404(
            UploadedFile,
            id=file_id,
            file_upload_state=UploadedFile.UPLOAD_STATES.AWAIT_COMPLETE
        )
        uploaded_file.completed_upload()
        return Response({
            'status': UploadedFile.UPLOAD_STATES.COMPLETED
        })


class UploadedFileFetchView(views.APIView):
    def get(self, request, file_id):
        uploaded_file = get_object_or_404(
            UploadedFile,
            id=file_id
        )
        return HttpResponseRedirect(uploaded_file.get_download_url())
