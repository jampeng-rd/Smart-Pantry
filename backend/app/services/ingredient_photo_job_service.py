"""Ingredient photo job 商業邏輯服務。"""

from fastapi import HTTPException, UploadFile, status

from backend.app.domain.schemas.ingredient_photo_job_schema import (
    IngredientPhotoJobCreateResponseData,
    IngredientPhotoJobStatusResponseData,
)
from backend.app.infra.repository.ai_job_repository import AiJobRepository
from backend.app.infra.storage import LocalStorage


class IngredientPhotoJobService:
    """處理 ingredient photo job 的建立與查詢。"""

    allowed_mime_types = {"image/jpeg", "image/png", "image/webp"}
    max_size_bytes = 5 * 1024 * 1024

    def __init__(self, ai_job_repository: AiJobRepository, storage: LocalStorage):
        """建立 IngredientPhotoJobService 實例。"""
        self.ai_job_repository = ai_job_repository
        self.storage = storage

    def create_photo_job(self, user_id: int, image: UploadFile) -> IngredientPhotoJobCreateResponseData:
        """建立食材照片辨識 job。"""
        self._validate_image(image=image)
        stored = self.storage.save_upload_file(upload_file=image, subdir="ingredient_photos")
        if stored.size_bytes > self.max_size_bytes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="圖片大小不可超過 5MB")

        input_snapshot = {
            "image_path": stored.image_path,
            "original_filename": stored.original_filename,
            "mime_type": stored.mime_type,
            "size_bytes": stored.size_bytes,
        }
        job = self.ai_job_repository.create_job(
            user_id=user_id,
            job_type="ingredient_photo",
            status="pending",
            input_snapshot=input_snapshot,
        )
        return IngredientPhotoJobCreateResponseData(job_id=job.id, status=job.status, created_at=job.created_at)

    def get_photo_job_status(self, user_id: int, job_id: int) -> IngredientPhotoJobStatusResponseData:
        """取得目前登入使用者的 ingredient photo job 狀態。"""
        job = self.ai_job_repository.get_job_by_id_and_user_id(job_id=job_id, user_id=user_id)
        if job is None or job.job_type != "ingredient_photo":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="找不到對應的 AI 任務")
        return IngredientPhotoJobStatusResponseData(
            job_id=job.id,
            status=job.status,
            result=job.result,
            error_message=job.error_message if job.status == "failed" else None,
            created_at=job.created_at,
            started_at=job.started_at,
            finished_at=job.finished_at,
        )

    def _validate_image(self, image: UploadFile) -> None:
        """驗證圖片格式與大小。"""
        if image.content_type not in self.allowed_mime_types:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支援的圖片格式，僅接受 JPEG/PNG/WEBP")

        image.file.seek(0, 2)
        size_bytes = image.file.tell()
        image.file.seek(0)
        if size_bytes > self.max_size_bytes:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="圖片大小不可超過 5MB")
