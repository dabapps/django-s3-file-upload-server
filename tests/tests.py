from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from model_mommy import mommy
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient
from rest_framework import serializers
from unittest.mock import patch, MagicMock

from s3_file_uploads.models import UploadedFile
from s3_file_uploads.fields import UploadedFilePrimaryKeyRelatedField


class UploadedFileTestSerialiser(serializers.Serializer):
    test_field = UploadedFilePrimaryKeyRelatedField()


class BaseTestCase(TestCase):
    EMAIL = 'dogs@llamas.com'
    PASSWORD = 'Reelsecure123'

    def setUp(self):
        super().setUp()
        self.api_client = APIClient()
        self.user = mommy.make(
            User,
            username=self.EMAIL,
        )
        self.user.set_password(self.PASSWORD)
        self.user.save()
        self.api_client.login(
            username=self.EMAIL,
            password=self.PASSWORD
        )


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
        self.assertEqual(new_file.user, self.user)
        self.assertEqual(response.data['id'], str(new_file.id))
        self.assertEqual(response.data['upload_form']['url'], "https://cat.com/a/b/")
        self.assertEqual(response.data['file'], "https://cat.com/b/a/")
        self.assertEqual(new_file.get_view_url(), response.data['file'])
        self.assertEqual(new_file.get_upload_form(), response.data['upload_form'])

    @patch('boto3.client')
    def test_complete_url_with_acl_data(self, boto_client_mock):
        acl_type = {'acl': 'public-read'}
        boto_client_mock.return_value.generate_presigned_url.return_value = "https://cat.com/b/a/"
        boto_client_mock.return_value.generate_presigned_post.return_value = "https://cat.com/b/a/"
        response = self.api_client.post(reverse('s3_file_uploads:upload-file-create'), data=acl_type)
        new_file = UploadedFile.objects.first()
        boto_client_mock.return_value.generate_presigned_post.assert_called_with(
            'AWS_BUCKET_NAME',
            str(new_file.id),
            Conditions=[acl_type, ['content-length-range', 1, 10485760]],
            ExpiresIn=300,
            Fields={'acl': 'public-read'},
        )
        self.assertEqual(new_file.get_upload_form(), response.data['upload_form'])

    @patch('boto3.client')
    def test_complete_url_with_no_acl_data(self, boto_client_mock):
        boto_client_mock.return_value.generate_presigned_url.return_value = "https://cat.com/b/a/"
        boto_client_mock.return_value.generate_presigned_post.return_value = "https://cat.com/b/a/"
        response = self.api_client.post(reverse('s3_file_uploads:upload-file-create'))
        new_file = UploadedFile.objects.first()
        boto_client_mock.return_value.generate_presigned_post.assert_called_with(
            'AWS_BUCKET_NAME',
            str(new_file.id),
            Conditions=[{'acl': 'private'}, ['content-length-range', 1, 10485760]],
            ExpiresIn=300,
            Fields={'acl': 'private'},
        )
        self.assertEqual(new_file.get_upload_form(), response.data['upload_form'])

    @patch('boto3.client')
    def test_complete_url_with_invalid_acl_data(self, boto_client_mock):
        acl_type = {'acl': 'invalid-acl-type'}
        boto_client_mock.return_value.generate_presigned_url.return_value = "https://cat.com/b/a/"
        boto_client_mock.return_value.generate_presigned_post.return_value = "https://cat.com/b/a/"
        response = self.api_client.post(reverse('s3_file_uploads:upload-file-create'), data=acl_type)
        self.assertEqual(
            response.data,
            {'acl': [ErrorDetail(string='"invalid-acl-type" is not a valid choice.', code='invalid_choice')]}
        )

    @patch('boto3.client')
    def test_complete_url(self, boto_client_mock):
        boto_client_mock.return_value.generate_presigned_url.return_value = "https://cat.com/b/a/"
        boto_client_mock.return_value.generate_presigned_post.return_value = "https://cat.com/b/a/"
        response = self.api_client.post(reverse('s3_file_uploads:upload-file-create'))
        new_file = UploadedFile.objects.first()
        self.assertEqual(new_file.file_upload_state, UploadedFile.UPLOAD_STATES.AWAIT_COMPLETE)
        response = self.api_client.post(response.data['complete_url'])
        self.assertEqual(response.status_code, 200)
        new_file.refresh_from_db()
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
        self.uploaded_file.refresh_from_db()
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


class UploadedFilePrimaryKeyRelatedFieldTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.valid_user = mommy.make(User)
        self.in_valid_user = mommy.make(User)
        self.uploaded_file = mommy.make(
            UploadedFile,
            file_upload_state=UploadedFile.UPLOAD_STATES.COMPLETED,
            file_key='file key',
            filename='foo.pdf',
            user=self.valid_user
        )

    def test_user_is_valid(self):
        mock_request = MagicMock()
        mock_request.user = self.valid_user
        serializer = UploadedFileTestSerialiser(
            data={'test_field': self.uploaded_file.id}, context={'request': mock_request}
        )
        self.assertTrue(serializer.is_valid())

    def test_user_is_not_valid(self):
        mock_request = MagicMock()
        mock_request.user = self.in_valid_user
        serializer = UploadedFileTestSerialiser(
            data={'test_field': self.uploaded_file.id}, context={'request': mock_request}
        )
        self.assertFalse(serializer.is_valid())
