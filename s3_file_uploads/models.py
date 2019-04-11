import uuid
from django.db import models
from django.urls import reverse
from django_fsm import FSMField, transition, ConcurrentTransitionMixin
from model_utils import Choices

from s3_file_uploads.aws import S3AssetHandler


class UploadedFile(ConcurrentTransitionMixin, models.Model):
    UPLOAD_STATES = Choices(
        ('NEW', 'New'),
        ('AWAIT_COMPLETE', 'Awaiting Completion'),
        ('COMPLETED', 'Completed')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    modified = models.DateTimeField(auto_now=True)

    file_key = models.CharField(max_length=255, blank=True)
    filename = models.CharField(max_length=255, blank=True)
    file_upload_state = FSMField(default=UPLOAD_STATES.NEW)

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

    def get_upload_form(self) -> dict:
        form = self.trans_get_upload_form()
        self.save()
        return form

    @transition(field=file_upload_state, source=[UPLOAD_STATES.NEW, UPLOAD_STATES.AWAIT_COMPLETE], target=UPLOAD_STATES.AWAIT_COMPLETE)
    def trans_get_upload_form(self) -> dict:
        return self.asset_handler.get_upload_form()

    def completed_upload(self) -> None:
        self.trans_completed_upload()
        self.save()

    @transition(field=file_upload_state, source=UPLOAD_STATES.AWAIT_COMPLETE, target=UPLOAD_STATES.COMPLETED)
    def trans_completed_upload(self) -> None:
        pass

    @transition(field=file_upload_state, source=[UPLOAD_STATES.NEW, UPLOAD_STATES.COMPLETED], target=UPLOAD_STATES.AWAIT_COMPLETE)
    def permit_reupload(self) -> None:
        # by default we don't allow re-uploading, but you can explicitly call
        # this to allow it. Useful for when something invalid was uploaded and
        # you want them to be able to upload it again.
        pass

    def get_view_url(self) -> str:
        return self.asset_handler.get_view_url(str(self.filename))

    def get_download_url(self) -> str:
        return self.asset_handler.get_download_url(str(self.filename))
