import uuid
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django_fsm import FSMField, transition, ConcurrentTransitionMixin

from s3_file_uploads.aws import S3AssetHandler


USER_MODEL = get_user_model()


class UploadedFile(ConcurrentTransitionMixin, models.Model):
    NEW = 'NEW'
    AWAIT_COMPLETE = 'AWAIT_COMPLETE'
    COMPLETED = 'COMPLETED'
    UPLOAD_STATES = [
        (NEW, 'New'),
        (AWAIT_COMPLETE, 'Awaiting Completion'),
        (COMPLETED, 'Completed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True)

    file_key = models.CharField(max_length=255, blank=True)
    filename = models.CharField(max_length=255, blank=True)
    file_upload_state = FSMField(default=NEW)

    user = models.ForeignKey(
        USER_MODEL,
        related_name='uploaded_files',
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        ordering = ['-created']

    @property
    def file_path(self):
        return reverse('s3_file_uploads:upload-file-fetch', args=(str(self.id),))

    def get_file_key(self):
        return str(self.file_key or self.id)

    @property
    def asset_handler(self):
        return S3AssetHandler(self.get_file_key())

    def get_upload_form(self, *args, **kwargs) -> dict:
        form = self.trans_get_upload_form(*args, **kwargs)
        self.save()
        return form

    @transition(field=file_upload_state, source=[NEW, AWAIT_COMPLETE], target=AWAIT_COMPLETE)
    def trans_get_upload_form(self, *args, **kwargs) -> dict:
        return self.asset_handler.get_upload_form(*args, **kwargs)

    def completed_upload(self) -> None:
        self.trans_completed_upload()
        self.save()

    @transition(field=file_upload_state, source=AWAIT_COMPLETE, target=COMPLETED)
    def trans_completed_upload(self) -> None:
        pass

    @transition(field=file_upload_state, source=[NEW, COMPLETED], target=AWAIT_COMPLETE)
    def permit_reupload(self) -> None:
        # by default we don't allow re-uploading, but you can explicitly call
        # this to allow it. Useful for when something invalid was uploaded and
        # you want them to be able to upload it again.
        pass

    def get_view_url(self) -> str:
        return self.asset_handler.get_view_url(str(self.filename))

    def get_download_url(self) -> str:
        return self.asset_handler.get_download_url(str(self.filename))
