import { useEffect, useMemo, useState, type FormEvent } from "react";
import { FiSave, FiX } from "react-icons/fi";

import type { ShoppingCreatePayload, ShoppingItem } from "../../features/shopping/shoppingTypes";

interface ShoppingFormDrawerProps {
  open: boolean;
  loading: boolean;
  initialItem: ShoppingItem | null;
  onClose: () => void;
  onSubmit: (payload: ShoppingCreatePayload) => Promise<void>;
}

interface ShoppingFormState {
  name: string;
  quantity: string;
  unit: string;
}

const defaultFormState: ShoppingFormState = {
  name: "",
  quantity: "1",
  unit: "",
};

/** 新增/編輯購物項目表單抽屜。 */
export function ShoppingFormDrawer({ open, loading, initialItem, onClose, onSubmit }: ShoppingFormDrawerProps) {
  const [form, setForm] = useState<ShoppingFormState>(defaultFormState);
  const [errors, setErrors] = useState<{ name?: string; quantity?: string; unit?: string }>({});

  const modeText = useMemo(() => (initialItem ? "編輯購物項目" : "新增購物項目"), [initialItem]);

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
      quantity: String(initialItem.quantity),
      unit: initialItem.unit,
    });
  }, [open, initialItem]);

  if (!open) {
    return null;
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const nextErrors: { name?: string; quantity?: string; unit?: string } = {};

    if (!form.name.trim()) {
      nextErrors.name = "請輸入項目名稱";
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

    if (!form.unit.trim()) {
      nextErrors.unit = "請輸入單位";
    }

    if (nextErrors.name || nextErrors.quantity || nextErrors.unit) {
      setErrors(nextErrors);
      return;
    }

    setErrors({});

    await onSubmit({
      name: form.name.trim(),
      quantity: Number(form.quantity),
      unit: form.unit.trim(),
    });
  };

  return (
    <>
      <button type="button" className="drawer-overlay" aria-label="關閉表單" onClick={onClose} />
      <aside className="shopping-drawer" aria-label={modeText}>
        <header className="shopping-drawer-header">
          <h3>{modeText}</h3>
          <button type="button" className="icon-btn" aria-label="關閉表單" onClick={onClose}>
            <FiX aria-hidden="true" />
          </button>
        </header>

        <form className="shopping-form" noValidate onSubmit={handleSubmit}>
          <label>
            項目名稱 *
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
              aria-describedby={errors.name ? "shopping-name-error" : undefined}
            />
            {errors.name ? (
              <p id="shopping-name-error" className="shopping-field-error" role="alert">
                {errors.name}
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
              aria-describedby={errors.quantity ? "shopping-quantity-error" : undefined}
            />
            {errors.quantity ? (
              <p id="shopping-quantity-error" className="shopping-field-error" role="alert">
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
              aria-describedby={errors.unit ? "shopping-unit-error" : undefined}
            />
            {errors.unit ? (
              <p id="shopping-unit-error" className="shopping-field-error" role="alert">
                {errors.unit}
              </p>
            ) : null}
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
