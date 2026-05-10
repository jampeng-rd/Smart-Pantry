"""AI job 資料存取層。"""

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.domain.models.ai_job_model import AiJob
from backend.app.domain.models.pantry_item_model import PantryItem
from backend.app.domain.schemas.recipe_job_schema import JobStatus, JobType


class AiJobRepository:
    """封裝 ai_jobs 與關聯 pantry 查詢。"""

    def __init__(self, db: Session):
        """建立 repository 實例。"""
        self.db = db

    def create_job(self, user_id: int, job_type: JobType, status: JobStatus, input_snapshot: dict) -> AiJob:
        """建立 AI job 記錄。"""
        job = AiJob(
            user_id=user_id,
            job_type=job_type,
            status=status,
            input_snapshot=input_snapshot,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_job_by_id_and_user_id(self, job_id: int, user_id: int) -> AiJob | None:
        """依 job_id 與 user_id 查詢 job。"""
        statement = select(AiJob).where(AiJob.id == job_id, AiJob.user_id == user_id)
        return self.db.execute(statement).scalar_one_or_none()

    def list_pantry_items_by_ids_and_user_id(self, item_ids: list[int], user_id: int) -> list[PantryItem]:
        """查詢屬於指定使用者的 pantry items。"""
        if not item_ids:
            return []
        statement = select(PantryItem).where(PantryItem.user_id == user_id, PantryItem.id.in_(item_ids)).order_by(PantryItem.id.asc())
        return list(self.db.execute(statement).scalars().all())

    def claim_pending_jobs(self, batch_size: int, job_types: list[str]) -> list[AiJob]:
        """一次 claim 一批 pending jobs，並依 job_type 過濾。"""
        if not job_types:
            return []

        statement = (
            select(AiJob)
            .where(AiJob.status == "pending", AiJob.job_type.in_(job_types))
            .order_by(AiJob.created_at.asc(), AiJob.id.asc())
            .limit(batch_size)
        )
        jobs = list(self.db.execute(statement).scalars().all())
        now = datetime.now(timezone.utc)
        claimed: list[AiJob] = []

        for job in jobs:
            current = self.db.get(AiJob, job.id)
            if current is None or current.status != "pending":
                continue
            current.status = "running"
            current.started_at = now
            current.finished_at = None
            current.error_message = None
            current.result = None
            claimed.append(current)

        self.db.commit()
        return claimed
