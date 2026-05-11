import { ChangeEvent, useEffect, useMemo, useRef, useState } from "react";
import { FiAlertCircle, FiCamera, FiCheckCircle, FiImage, FiLoader, FiPlusCircle, FiTrash2, FiUpload } from "react-icons/fi";

import { useAppDispatch, useAppSelector } from "../app/hooks";
import { EmptyState } from "../components/common/EmptyState";
import { ErrorState } from "../components/common/ErrorState";
import {
  clearIngredientJobError,
  confirmCandidatesToPantry,
  createIngredientPhotoJob,
  fetchIngredientPhotoJobStatus,
  removeCandidate,
  updateCandidateField,
} from "../features/ingredients/ingredientSlice";
import type { IngredientCandidateItem } from "../features/ingredients/ingredientTypes";

const MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024;
const ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/webp"];
const POLLING_INTERVAL_MS = 2500;

/** 食材辨識頁：上傳圖片、輪詢 job、確認候選後寫入 pantry。 */
export function IngredientsPage() {
  const dispatch = useAppDispatch();
  const { uploading, polling, currentJobId, jobStatus, jobError, candidates, resultNote, confirmLoading, confirmSummary } = useAppSelector(
    (state) => state.ingredients,
  );
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const intervalRef = useRef<number | null>(null);

  useEffect(() => {
    if (!currentJobId) {
      return;
    }
    if (jobStatus === "pending" || jobStatus === "running") {
      void dispatch(fetchIngredientPhotoJobStatus(currentJobId));
    }
  }, [dispatch, currentJobId, jobStatus]);

  useEffect(() => {
    if (!currentJobId || !polling) {
      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      return;
    }
    if (intervalRef.current !== null) {
      window.clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    intervalRef.current = window.setInterval(() => {
      void dispatch(fetchIngredientPhotoJobStatus(currentJobId));
    }, POLLING_INTERVAL_MS);

    return () => {
      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [dispatch, polling, currentJobId]);

  useEffect(() => {
    return () => {
      if (intervalRef.current !== null) {
        window.clearInterval(intervalRef.current);
      }
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
      }
    };
  }, [previewUrl]);

  const pendingMessage = useMemo(() => {
    if (jobStatus === "running") {
      return "AI 正在辨識食材";
    }
    if (jobStatus === "pending") {
      return "AI 正在辨識食材";
    }
    return null;
  }, [jobStatus]);

  const onFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    setFileError(null);
    setFormError(null);
    if (!file) {
      setSelectedFile(null);
      if (previewUrl) {
        URL.revokeObjectURL(previewUrl);
        setPreviewUrl(null);
      }
      return;
    }
    if (!ALLOWED_MIME_TYPES.includes(file.type)) {
      setFileError("圖片格式不支援，請使用 JPG、PNG 或 WEBP。");
      return;
    }
    if (file.size > MAX_IMAGE_SIZE_BYTES) {
      setFileError("圖片大小不可超過 5MB，請改用較小檔案。");
      return;
    }

    setSelectedFile(file);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
    }
    setPreviewUrl(URL.createObjectURL(file));
  };

  const onCreateJob = async () => {
    setFileError(null);
    setFormError(null);
    if (!selectedFile) {
      setFileError("請先選擇一張圖片。");
      return;
    }
    await dispatch(createIngredientPhotoJob(selectedFile)).unwrap();
  };

  const onCandidateChange = (index: number, field: keyof IngredientCandidateItem, value: string) => {
    if (field === "quantity") {
      const parsed = Number.parseFloat(value);
      dispatch(updateCandidateField({ index, field, value: Number.isFinite(parsed) ? parsed : 0 }));
      return;
    }
    if (field === "expiration_date") {
      dispatch(updateCandidateField({ index, field, value: value.trim() ? value : null }));
      return;
    }
    dispatch(updateCandidateField({ index, field, value }));
  };

  const validateCandidates = (items: IngredientCandidateItem[]): string | null => {
    for (let index = 0; index < items.length; index += 1) {
      const item = items[index];
      if (!item.name.trim() || !item.category.trim() || !item.unit.trim()) {
        return `第 ${index + 1} 筆候選食材的名稱、分類、數量、單位為必填。`;
      }
      if (!Number.isFinite(item.quantity) || item.quantity <= 0) {
        return `第 ${index + 1} 筆候選食材的數量必須大於 0。`;
      }
    }
    return null;
  };

  const onConfirmToPantry = async () => {
    setFormError(null);
    const validationError = validateCandidates(candidates);
    if (validationError) {
      setFormError(validationError);
      return;
    }
    await dispatch(confirmCandidatesToPantry(candidates)).unwrap();
  };

  return (
    <section className="workspace-ingredients">
      <div className="card ingredients-upload-card">
        <h2 className="workspace-title">
          <FiCamera aria-hidden="true" /> 食材辨識
        </h2>
        <p className="ingredients-tip">
          建議拍攝單一或少量未加工食材。避免整桌料理、冰箱全景、多人餐點或過多品項。
        </p>
        <div className="ingredients-upload-row">
          <label className="btn ghost ingredients-file-label" htmlFor="ingredient-image-input">
            <FiImage aria-hidden="true" /> 選擇圖片
          </label>
          <input
            id="ingredient-image-input"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={onFileChange}
            className="ingredients-file-input"
          />
          <button type="button" className="btn" onClick={() => void onCreateJob()} disabled={uploading || polling || !selectedFile}>
            {uploading ? <FiLoader aria-hidden="true" className="spin" /> : <FiUpload aria-hidden="true" />}
            建立辨識任務
          </button>
        </div>
        {selectedFile ? <p className="muted-text">已選擇：{selectedFile.name}</p> : null}
        {fileError ? <p className="pantry-field-error">{fileError}</p> : null}
        {previewUrl ? <img src={previewUrl} alt="食材預覽" className="ingredients-preview" /> : null}
      </div>

      {pendingMessage ? (
        <div className="card ingredients-status" role="status">
          <FiLoader aria-hidden="true" className="spin" />
          <p>{pendingMessage}</p>
        </div>
      ) : null}

      {jobError ? (
        <ErrorState
          message={jobError}
          className="card pantry-error"
          actionsClassName="pantry-error-actions"
          onClose={() => dispatch(clearIngredientJobError())}
        />
      ) : null}

      {jobStatus === "success" && candidates.length === 0 ? (
        <EmptyState
          icon={FiAlertCircle}
          title="沒有可用候選食材"
          description="此張圖片暫時未辨識出候選食材，請改用較清楚、單一或少量食材的照片。"
          className="card pantry-empty"
        />
      ) : null}

      {jobStatus === "success" && candidates.length > 0 ? (
        <div className="card ingredients-candidates-card">
          <header className="ingredients-candidate-header">
            <h3>
              <FiCheckCircle aria-hidden="true" /> 候選食材（請確認後加入庫存）
            </h3>
            <button type="button" className="btn" onClick={() => void onConfirmToPantry()} disabled={confirmLoading}>
              {confirmLoading ? <FiLoader aria-hidden="true" className="spin" /> : <FiPlusCircle aria-hidden="true" />}
              確認加入庫存
            </button>
          </header>
          {resultNote ? <p className="muted-text">{resultNote}</p> : null}
          {formError ? <p className="pantry-field-error">{formError}</p> : null}
          <div className="ingredients-candidates-list">
            {candidates.map((candidate, index) => (
              <article key={`${candidate.name}-${index}`} className="ingredients-candidate-item">
                <div className="ingredients-candidate-item-head">
                  <strong>候選 {index + 1}</strong>
                  <button
                    type="button"
                    className="icon-btn"
                    aria-label={`刪除候選食材 ${candidate.name || index + 1}`}
                    onClick={() => dispatch(removeCandidate(index))}
                  >
                    <FiTrash2 aria-hidden="true" />
                  </button>
                </div>
                <div className="ingredients-candidate-grid">
                  <label>
                    名稱*
                    <input value={candidate.name} onChange={(event) => onCandidateChange(index, "name", event.target.value)} />
                  </label>
                  <label>
                    分類*
                    <input value={candidate.category} onChange={(event) => onCandidateChange(index, "category", event.target.value)} />
                  </label>
                  <label>
                    數量*
                    <input
                      type="number"
                      min="0"
                      step="0.1"
                      value={candidate.quantity}
                      onChange={(event) => onCandidateChange(index, "quantity", event.target.value)}
                    />
                  </label>
                  <label>
                    單位*
                    <input value={candidate.unit} onChange={(event) => onCandidateChange(index, "unit", event.target.value)} />
                  </label>
                  <label>
                    到期日
                    <input
                      type="date"
                      value={candidate.expiration_date ?? ""}
                      onChange={(event) => onCandidateChange(index, "expiration_date", event.target.value)}
                    />
                  </label>
                  <label>
                    儲存位置
                    <input
                      value={candidate.storage_location}
                      onChange={(event) => onCandidateChange(index, "storage_location", event.target.value)}
                    />
                  </label>
                  <label className="ingredients-candidate-note">
                    備註
                    <input value={candidate.note} onChange={(event) => onCandidateChange(index, "note", event.target.value)} />
                  </label>
                </div>
              </article>
            ))}
          </div>

          {confirmSummary ? (
            <div className="ingredients-confirm-summary" role="status">
              <p>成功加入 {confirmSummary.successCount} 筆食材到庫存。</p>
              {confirmSummary.failureItems.length > 0 ? (
                <ul>
                  {confirmSummary.failureItems.map((failure) => (
                    <li key={`${failure.index}-${failure.name}`}>
                      {failure.name || `第 ${failure.index + 1} 筆`}：{failure.reason}
                    </li>
                  ))}
                </ul>
              ) : null}
            </div>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}
