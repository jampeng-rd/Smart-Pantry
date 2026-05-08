import { useEffect, useMemo, useState, type FormEvent } from "react";
import { FiSave, FiX } from "react-icons/fi";

import type { PantryCreatePayload } from "../../features/pantry/pantryTypes";
import type { ShoppingItem } from "../../features/shopping/shoppingTypes";

interface ShoppingToPantryDrawerProps {
  open: boolean;
  loading: boolean;
  item: ShoppingItem | null;
  onClose: () => void;
  onSubmit: (payload: PantryCreatePayload) => Promise<void>;
}

interface ShoppingToPantryFormState {
  name: string;
  quantity: string;
  unit: string;
  category: string;
  expiration_date: string;
  storage_location: string;
  note: string;
}

const defaultFormState: ShoppingToPantryFormState = {
  name: "",
  quantity: "1",
  unit: "",
  category: "",
  expiration_date: "",
  storage_location: "",
  note: "",
};

/** 將已購買購物項目加入庫存前的人工確認抽屜。 */
export function ShoppingToPantryDrawer({ open, loading, item, onClose, onSubmit }: ShoppingToPantryDrawerProps) {
  const [form, setForm] = useState<ShoppingToPantryFormState>(defaultFormState);
  const [errors, setErrors] = useState<{ name?: string; quantity?: string; category?: string }>({});

  const title = useMemo(() => "確認加入庫存", []);

  useEffect(() => {
    if (!open || !item) {
      setErrors({});
      if (!open) {
        setForm(defaultFormState);
      }
      return;
    }

    setForm({
      name: item.name,
      quantity: String(item.quantity),
      unit: item.unit,
      category: "",
      expiration_date: "",
      storage_location: "",
      note: "",
    });
  }, [open, item]);

  if (!open || !item) {
    return null;
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const nextErrors: { name?: string; quantity?: string; category?: string } = {};

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
      if (!Number.isFinite(quantity) || !Number.isInteger(quantity)) {
        nextErrors.quantity = "數量必須是整數";
      } else if (quantity < 1) {
        nextErrors.quantity = "數量必須大於或等於 1";
      }
    }

    if (nextErrors.name || nextErrors.quantity || nextErrors.category) {
      setErrors(nextErrors);
      return;
    }

    setErrors({});

    await onSubmit({
      name: form.name.trim(),
      category: form.category.trim(),
      quantity: Number(form.quantity),
      unit: form.unit.trim(),
      expiration_date: form.expiration_date || null,
      storage_location: form.storage_location.trim() || null,
      note: form.note.trim() || null,
    });
  };

  return (
    <>
      <button type="button" className="drawer-overlay" aria-label="關閉加入庫存確認" onClick={onClose} />
      <aside className="pantry-drawer" aria-label={title}>
        <header className="pantry-drawer-header">
          <h3>{title}</h3>
          <button type="button" className="icon-btn" aria-label="關閉加入庫存確認" onClick={onClose}>
            <FiX aria-hidden="true" />
          </button>
        </header>

        <form className="pantry-form" noValidate onSubmit={handleSubmit}>
          <p className="integration-tip">此操作不會自動更新原購物項目，請先確認資料後再加入庫存。</p>

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
              aria-describedby={errors.name ? "shopping-to-pantry-name-error" : undefined}
            />
            {errors.name ? (
              <p id="shopping-to-pantry-name-error" className="pantry-field-error" role="alert">
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
              aria-describedby={errors.category ? "shopping-to-pantry-category-error" : undefined}
            />
            {errors.category ? (
              <p id="shopping-to-pantry-category-error" className="pantry-field-error" role="alert">
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
              aria-describedby={errors.quantity ? "shopping-to-pantry-quantity-error" : undefined}
            />
            {errors.quantity ? (
              <p id="shopping-to-pantry-quantity-error" className="pantry-field-error" role="alert">
                {errors.quantity}
              </p>
            ) : null}
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

          <button type="submit" className="btn primary" disabled={loading}>
            <FiSave aria-hidden="true" />
            {loading ? "加入中..." : "確認加入庫存"}
          </button>
        </form>
      </aside>
    </>
  );
}
