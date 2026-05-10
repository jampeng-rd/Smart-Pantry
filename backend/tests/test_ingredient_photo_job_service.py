"""Ingredient photo job 服務測試。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

import pytest
from fastapi import HTTPException, UploadFile
from starlette.datastructures import Headers

from backend.app.services.ingredient_photo_job_service import IngredientPhotoJobService


@dataclass
class FakeAiJob:
    """測試用 ai job。"""

    id: int
    user_id: int
    job_type: str
    status: str
    input_snapshot: dict
    result: dict | None
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class FakeAiJobRepository:
    """以記憶體模擬 AiJobRepository。"""

    def __init__(self) -> None:
        self.jobs: dict[int, FakeAiJob] = {}
        self._seq = 1

    def create_job(self, user_id: int, job_type: str, status: str, input_snapshot: dict) -> FakeAiJob:
        job = FakeAiJob(
            id=self._seq,
            user_id=user_id,
            job_type=job_type,
            status=status,
            input_snapshot=input_snapshot,
            result=None,
            error_message=None,
            created_at=datetime.now(timezone.utc),
            started_at=None,
            finished_at=None,
        )
        self.jobs[self._seq] = job
        self._seq += 1
        return job

    def get_job_by_id_and_user_id(self, job_id: int, user_id: int) -> FakeAiJob | None:
        job = self.jobs.get(job_id)
        if job is None or job.user_id != user_id:
            return None
        return job


class FakeStorage:
    """測試用本機儲存 fake。"""

    def __init__(self, root: Path):
        self.root = root

    def save_upload_file(self, upload_file: UploadFile, subdir: str):
        target_dir = self.root / subdir
        target_dir.mkdir(parents=True, exist_ok=True)
        content = upload_file.file.read()
        upload_file.file.seek(0)
        target = target_dir / "mock_saved.jpg"
        target.write_bytes(content)
        return type(
            "StoredFileInfo",
            (),
            {
                "image_path": str(target),
                "original_filename": upload_file.filename or "unknown",
                "mime_type": upload_file.content_type or "application/octet-stream",
                "size_bytes": len(content),
            },
        )()


def _make_upload_file(filename: str, content: bytes, mime_type: str) -> UploadFile:
    """建立測試 UploadFile。"""
    headers = Headers({"content-type": mime_type})
    return UploadFile(file=BytesIO(content), filename=filename, headers=headers)


@pytest.fixture
def ingredient_job_service(tmp_path: Path) -> tuple[IngredientPhotoJobService, FakeAiJobRepository]:
    """建立 IngredientPhotoJobService 與假 repository。"""
    repository = FakeAiJobRepository()
    storage = FakeStorage(root=tmp_path / "uploads")
    return IngredientPhotoJobService(ai_job_repository=repository, storage=storage), repository


def test_upload_image_can_create_ingredient_photo_job(ingredient_job_service: tuple[IngredientPhotoJobService, FakeAiJobRepository]) -> None:
    """上傳圖片可建立 ingredient_photo job。"""
    service, repository = ingredient_job_service
    upload = _make_upload_file("ingredient.jpg", b"fake-image", "image/jpeg")

    result = service.create_photo_job(user_id=1, image=upload)

    assert result.status == "pending"
    job = repository.jobs[result.job_id]
    assert job.job_type == "ingredient_photo"
    assert "image_path" in job.input_snapshot
    assert "mime_type" in job.input_snapshot
    assert "size_bytes" in job.input_snapshot
    assert "blob" not in job.input_snapshot
    assert "base64" not in job.input_snapshot


def test_upload_image_larger_than_5mb_should_fail(ingredient_job_service: tuple[IngredientPhotoJobService, FakeAiJobRepository]) -> None:
    """超過 5MB 圖片應拒絕。"""
    service, _ = ingredient_job_service
    upload = _make_upload_file("big.jpg", b"x" * (5 * 1024 * 1024 + 1), "image/jpeg")

    with pytest.raises(HTTPException) as exc:
        service.create_photo_job(user_id=1, image=upload)

    assert exc.value.status_code == 400
    assert "5MB" in str(exc.value.detail)


def test_upload_unsupported_mime_type_should_fail(ingredient_job_service: tuple[IngredientPhotoJobService, FakeAiJobRepository]) -> None:
    """不支援 mime type 應拒絕。"""
    service, _ = ingredient_job_service
    upload = _make_upload_file("ingredient.gif", b"gif-content", "image/gif")

    with pytest.raises(HTTPException) as exc:
        service.create_photo_job(user_id=1, image=upload)

    assert exc.value.status_code == 400
    assert "不支援的圖片格式" in str(exc.value.detail)


def test_get_job_should_not_allow_cross_user_access(ingredient_job_service: tuple[IngredientPhotoJobService, FakeAiJobRepository]) -> None:
    """GET job 不可跨 user 查詢。"""
    service, _ = ingredient_job_service
    upload = _make_upload_file("ingredient.jpg", b"fake-image", "image/jpeg")
    created = service.create_photo_job(user_id=1, image=upload)

    with pytest.raises(HTTPException) as exc:
        service.get_photo_job_status(user_id=2, job_id=created.job_id)

    assert exc.value.status_code == 404


def test_pending_and_running_result_should_be_null(ingredient_job_service: tuple[IngredientPhotoJobService, FakeAiJobRepository]) -> None:
    """pending/running 時 result 應為 null。"""
    service, repository = ingredient_job_service
    upload = _make_upload_file("ingredient.jpg", b"fake-image", "image/jpeg")
    created = service.create_photo_job(user_id=1, image=upload)

    pending_payload = service.get_photo_job_status(user_id=1, job_id=created.job_id)
    assert pending_payload.status == "pending"
    assert pending_payload.result is None

    repository.jobs[created.job_id].status = "running"
    repository.jobs[created.job_id].result = None
    running_payload = service.get_photo_job_status(user_id=1, job_id=created.job_id)
    assert running_payload.status == "running"
    assert running_payload.result is None
