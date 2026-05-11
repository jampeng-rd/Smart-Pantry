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
  const [errors, setErrors] = useState<{ name?: string; category?: string; quantity?: string; unit?: string }>({});

  const modeText = useMemo(() => (initialItem ? "編輯食材" : "新增食材"), [initialItem]);

  useEffect(() => {
    if (!open) {
      setErrors({});
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
    const nextErrors: { name?: string; category?: string; quantity?: string; unit?: string } = {};

    if (!form.name.trim()) {
      nextErrors.name = "請輸入食材名稱";
    }

    if (!form.category.trim()) {
      nextErrors.category = "請輸入分類";
    }

    const quantityRaw = form.quantity.trim();
    if (!quantityRaw) {
      nextErrors.quantity = "請輸入數量";
    } else {
      const quantity = Number(quantityRaw);
      if (!Number.isFinite(quantity)) {
        nextErrors.quantity = "數量必須是整數";
      } else if (!Number.isInteger(quantity)) {
        nextErrors.quantity = "數量必須是整數";
      } else if (quantity < 1) {
        nextErrors.quantity = "數量必須大於或等於 1";
      }
    }

    if (!form.unit.trim()) {
      nextErrors.unit = "請輸入單位";
    }

    if (nextErrors.name || nextErrors.category || nextErrors.quantity || nextErrors.unit) {
      setErrors(nextErrors);
      return;
    }

    setErrors({});
    const quantity = Number(form.quantity);

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

        <form className="pantry-form" noValidate onSubmit={handleSubmit}>
          <label>
            食材名稱 *
            <input
              type="text"
              value={form.name}
              onChange={(event) => {
                const value = event.target.value;
                setForm((prev) => ({ ...prev, name: value }));
                if (errors.name && value.trim()) {
                  setErrors((prev) => ({ ...prev, name: undefined }));
                }
              }}
              aria-required="true"
              aria-invalid={Boolean(errors.name)}
              aria-describedby={errors.name ? "pantry-name-error" : undefined}
            />
            {errors.name ? (
              <p id="pantry-name-error" className="pantry-field-error" role="alert">
                {errors.name}
              </p>
            ) : null}
          </label>

          <label>
            分類 *
            <input
              type="text"
              value={form.category}
              onChange={(event) => {
                const value = event.target.value;
                setForm((prev) => ({ ...prev, category: value }));
                if (errors.category && value.trim()) {
                  setErrors((prev) => ({ ...prev, category: undefined }));
                }
              }}
              aria-required="true"
              aria-invalid={Boolean(errors.category)}
              aria-describedby={errors.category ? "pantry-category-error" : undefined}
            />
            {errors.category ? (
              <p id="pantry-category-error" className="pantry-field-error" role="alert">
                {errors.category}
              </p>
            ) : null}
          </label>

          <label>
            數量 *
            <input
              type="number"
              min={1}
              step={1}
              value={form.quantity}
              onChange={(event) => {
                const value = event.target.value;
                setForm((prev) => ({ ...prev, quantity: value }));
                if (errors.quantity && value.trim()) {
                  setErrors((prev) => ({ ...prev, quantity: undefined }));
                }
              }}
              aria-required="true"
              aria-invalid={Boolean(errors.quantity)}
              aria-describedby={errors.quantity ? "pantry-quantity-error" : undefined}
            />
            {errors.quantity ? (
              <p id="pantry-quantity-error" className="pantry-field-error" role="alert">
                {errors.quantity}
              </p>
            ) : null}
          </label>

          <label>
            單位 *
            <input
              type="text"
              value={form.unit}
              placeholder="例如 顆、包、瓶、份"
              onChange={(event) => {
                const value = event.target.value;
                setForm((prev) => ({ ...prev, unit: value }));
                if (errors.unit && value.trim()) {
                  setErrors((prev) => ({ ...prev, unit: undefined }));
                }
              }}
              aria-required="true"
              aria-invalid={Boolean(errors.unit)}
              aria-describedby={errors.unit ? "pantry-unit-error" : undefined}
            />
            {errors.unit ? (
              <p id="pantry-unit-error" className="pantry-field-error" role="alert">
                {errors.unit}
              </p>
            ) : null}
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

          <button type="submit" className="btn primary" disabled={loading}>
            <FiSave aria-hidden="true" />
            {loading ? "儲存中..." : "儲存"}
          </button>
        </form>
      </aside>
    </>
  );
}
