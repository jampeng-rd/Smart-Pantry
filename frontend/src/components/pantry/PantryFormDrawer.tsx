import { useEffect, useMemo, useState, type FormEvent } from "react";
import { FiSave, FiX } from "react-icons/fi";

import type { PantryCreatePayload, PantryItem } from "../../features/pantry/pantryTypes";

interface PantryFormDrawerProps {
  open: boolean;
  loading: boolean;
  initialItem: PantryItem | null;
  onClose: () => void;
  onSubmit: (payload: PantryCreatePayload) => Promise<void>;
}

interface PantryFormState {
  name: string;
  category: string;
  quantity: string;
  unit: string;
  expiration_date: string;
  storage_location: string;
  note: string;
}

const defaultFormState: PantryFormState = {
  name: "",
  category: "",
  quantity: "1",
  unit: "",
  expiration_date: "",
  storage_location: "",
  note: "",
};

/** 新增/編輯食材表單抽屜。 */
export function PantryFormDrawer({ open, loading, initialItem, onClose, onSubmit }: PantryFormDrawerProps) {
  const [form, setForm] = useState<PantryFormState>(defaultFormState);
  const [error, setError] = useState<string | null>(null);

  const modeText = useMemo(() => (initialItem ? "編輯食材" : "新增食材"), [initialItem]);

  useEffect(() => {
    if (!open) {
      setError(null);
      return;
    }

    if (!initialItem) {
      setForm(defaultFormState);
      return;
    }

    setForm({
      name: initialItem.name,
      category: initialItem.category,
      quantity: String(initialItem.quantity),
      unit: initialItem.unit,
      expiration_date: initialItem.expiration_date ?? "",
      storage_location: initialItem.storage_location ?? "",
      note: initialItem.note ?? "",
    });
  }, [open, initialItem]);

  if (!open) {
    return null;
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    const quantity = Number(form.quantity);
    if (!form.name.trim()) {
      setError("請輸入食材名稱");
      return;
    }
    if (!Number.isFinite(quantity) || !Number.isInteger(quantity) || quantity < 1) {
      setError("數量必須是大於等於 1 的整數");
      return;
    }

    await onSubmit({
      name: form.name.trim(),
      category: form.category.trim(),
      quantity,
      unit: form.unit.trim(),
      expiration_date: form.expiration_date || null,
      storage_location: form.storage_location.trim() || null,
      note: form.note.trim() || null,
    });
  };

  return (
    <>
      <button type="button" className="drawer-overlay" aria-label="關閉表單" onClick={onClose} />
      <aside className="pantry-drawer" aria-label={modeText}>
        <header className="pantry-drawer-header">
          <h3>{modeText}</h3>
          <button type="button" className="icon-btn" aria-label="關閉表單" onClick={onClose}>
            <FiX aria-hidden="true" />
          </button>
        </header>

        <form className="pantry-form" onSubmit={handleSubmit}>
          <label>
            食材名稱 *
            <input
              type="text"
              value={form.name}
              onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))}
              required
            />
          </label>

          <label>
            分類
            <input type="text" value={form.category} onChange={(event) => setForm((prev) => ({ ...prev, category: event.target.value }))} />
          </label>

          <label>
            數量 *
            <input
              type="number"
              min={1}
              step={1}
              value={form.quantity}
              onChange={(event) => setForm((prev) => ({ ...prev, quantity: event.target.value }))}
              required
            />
          </label>

          <label>
            單位
            <input type="text" value={form.unit} onChange={(event) => setForm((prev) => ({ ...prev, unit: event.target.value }))} />
          </label>

          <label>
            過期日
            <input
              type="date"
              value={form.expiration_date}
              onChange={(event) => setForm((prev) => ({ ...prev, expiration_date: event.target.value }))}
            />
          </label>

          <label>
            保存位置
            <input
              type="text"
              value={form.storage_location}
              onChange={(event) => setForm((prev) => ({ ...prev, storage_location: event.target.value }))}
            />
          </label>

          <label>
            備註
            <textarea value={form.note} onChange={(event) => setForm((prev) => ({ ...prev, note: event.target.value }))} rows={4} />
          </label>

          {error ? <p className="error-text">{error}</p> : null}

          <button type="submit" className="btn primary" disabled={loading}>
            <FiSave aria-hidden="true" />
            {loading ? "儲存中..." : "儲存"}
          </button>
        </form>
      </aside>
    </>
  );
}
