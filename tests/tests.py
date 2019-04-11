from django.test import TestCase
from django.urls import reverse
from model_mommy import mommy
from rest_framework.test import APIClient
from unittest.mock import patch

from s3_file_uploads.models import UploadedFile


def refresh_instance(instance):
    # refresh database model instance
    return instance.__class__.objects.get(id=instance.id)


class BaseTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.api_client = APIClient()


class UploadedFileTestCase(BaseTestCase):
    @patch('boto3.client')
    def test_upload_file(self, boto_client_mock):
        boto_client_mock.return_value.generate_presigned_url.return_value = "https://cat.com/b/a/"
        boto_client_mock.return_value.generate_presigned_post.return_value = {
            'url': "https://cat.com/a/b/"
        }
        response = self.api_client.post(reverse('s3_file_uploads:upload-file-create'))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(UploadedFile.objects.count(), 1)
        new_file = UploadedFile.objects.first()
        self.assertEqual(new_file.file_key, '')
        self.assertEqual(response.data['id'], str(new_file.id))
        self.assertEqual(response.data['upload_form']['url'], "https://cat.com/a/b/")
        self.assertEqual(response.data['file'], "https://cat.com/b/a/")
        self.assertEqual(new_file.get_view_url(), response.data['file'])
        self.assertEqual(new_file.get_upload_form(), response.data['upload_form'])

    @patch('boto3.client')
    def test_complete_url(self, boto_client_mock):
        boto_client_mock.return_value.generate_presigned_url.return_value = "https://cat.com/b/a/"
        boto_client_mock.return_value.generate_presigned_post.return_value = "https://cat.com/b/a/"
        response = self.api_client.post(reverse('s3_file_uploads:upload-file-create'))
        new_file = UploadedFile.objects.first()
        self.assertEqual(new_file.file_upload_state, UploadedFile.UPLOAD_STATES.AWAIT_COMPLETE)
        response = self.api_client.post(response.data['complete_url'])
        self.assertEqual(response.status_code, 200)
        new_file = refresh_instance(new_file)
        self.assertEqual(new_file.file_upload_state, UploadedFile.UPLOAD_STATES.COMPLETED)


class UploadedFileUploadCompleteViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.uploaded_file = mommy.make(
            UploadedFile,
            file_upload_state=UploadedFile.UPLOAD_STATES.AWAIT_COMPLETE
        )

    def test_completes(self):
        self.api_client.post(reverse('s3_file_uploads:upload-file-complete', kwargs={
            'file_id': str(self.uploaded_file.id)
        }))
        self.uploaded_file = refresh_instance(self.uploaded_file)
        self.assertEqual(self.uploaded_file.file_upload_state, UploadedFile.UPLOAD_STATES.COMPLETED)

    def test_cant_complete_in_wrong_state(self):
        self.uploaded_file.file_upload_state = UploadedFile.UPLOAD_STATES.COMPLETED
        self.uploaded_file.save()
        response = self.api_client.post(reverse('s3_file_uploads:upload-file-complete', kwargs={
            'file_id': str(self.uploaded_file.id)
        }))
        self.assertEqual(response.status_code, 404)

        self.uploaded_file.file_upload_state = UploadedFile.UPLOAD_STATES.NEW
        self.uploaded_file.save()
        response = self.api_client.post(reverse('s3_file_uploads:upload-file-complete', kwargs={
            'file_id': str(self.uploaded_file.id)
        }))
        self.assertEqual(response.status_code, 404)


class UploadedFileFetchViewTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.uploaded_file = mommy.make(
            UploadedFile,
            file_upload_state=UploadedFile.UPLOAD_STATES.COMPLETED,
            file_key='file key',
            filename='foo.pdf'
        )

    @patch('boto3.client')
    def test_fetch_file(self, boto_client_mock):
        boto_client_mock.return_value.generate_presigned_url.return_value = "https://cat.com/b/a/"
        response = self.api_client.get(reverse('s3_file_uploads:upload-file-fetch', kwargs={
            'file_id': str(self.uploaded_file.id)
        }))
        self.assertRedirects(response, "https://cat.com/b/a/", fetch_redirect_response=False)
