"""檔案儲存基礎設施。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4
import logging

from fastapi import UploadFile

LOGGER = logging.getLogger(__name__)


@dataclass
class StoredFileInfo:
    """儲存後檔案資訊。"""

    image_path: str
    original_filename: str
    mime_type: str
    size_bytes: int


class LocalStorage:
    """本機檔案儲存服務（MVP 開發階段）。"""

    def __init__(self, root_dir: str = "uploads") -> None:
        """建立本機儲存服務。"""
        self.root_dir = Path(root_dir)

    def save_upload_file(self, upload_file: UploadFile, subdir: str) -> StoredFileInfo:
        """將 UploadFile 儲存到本機，回傳儲存資訊。"""
        target_dir = self.root_dir / subdir
        target_dir.mkdir(parents=True, exist_ok=True)

        mime_type = upload_file.content_type or "application/octet-stream"
        extension = self._extension_from_mime_type(mime_type=mime_type)
        filename = f"{uuid4().hex}{extension}"
        target_path = target_dir / filename

        upload_file.file.seek(0)
        content = upload_file.file.read()
        size_bytes = len(content)
        with target_path.open("wb") as output:
            output.write(content)

        upload_file.file.seek(0)
        return StoredFileInfo(
            image_path=str(target_path),
            original_filename=upload_file.filename or "unknown",
            mime_type=mime_type,
            size_bytes=size_bytes,
        )

    def _extension_from_mime_type(self, mime_type: str) -> str:
        """依 mime type 回傳對應副檔名。"""
        mapping = {
            "image/jpeg": ".jpg",
            "image/png": ".png",
            "image/webp": ".webp",
        }
        return mapping.get(mime_type, ".bin")

    def delete_file(self, path: str) -> bool:
        """安全刪除 uploads 目錄下檔案，僅回傳是否成功刪除。"""
        if not path:
            return False

        root_resolved = self.root_dir.resolve()
        target_path = Path(path)
        if not target_path.is_absolute():
            target_path = Path.cwd() / target_path

        try:
            target_resolved = target_path.resolve()
        except OSError:
            LOGGER.warning("delete_file failed to resolve path=%s", path)
            return False

        if root_resolved not in target_resolved.parents:
            LOGGER.warning("delete_file blocked path outside uploads path=%s", path)
            return False

        if not target_resolved.exists():
            return False

        try:
            target_resolved.unlink()
            return True
        except OSError:
            LOGGER.warning("delete_file failed path=%s", path)
            return False
