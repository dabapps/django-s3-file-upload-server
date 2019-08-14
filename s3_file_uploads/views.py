from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, views
from rest_framework.response import Response
from django.urls import reverse
from s3_file_uploads.models import UploadedFile
from s3_file_uploads.serializers import UploadedFileSerializer


class UploadedFileCreateView(generics.CreateAPIView):
    serializer_class = UploadedFileSerializer

    def get_queryset(self):
        return UploadedFile.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer_data = {**request.data, 'user': request.user.id}
        serializer = self.get_serializer(data=serializer_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        uploaded_file = serializer.instance
        uploaded_file_data = UploadedFileSerializer(instance=uploaded_file).data
        uploaded_file_data['upload_form'] = uploaded_file.get_upload_form()
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
