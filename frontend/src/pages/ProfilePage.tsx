import { FormEvent, useEffect, useMemo, useState } from "react";
import { FiEye, FiEyeOff, FiKey, FiMail, FiSave, FiUser } from "react-icons/fi";

import { profileApi } from "../services/apiClient";
import type { ProfileData } from "../features/profile/profileTypes";

/** 個人資料頁面。 */
export function ProfilePage() {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [displayName, setDisplayName] = useState("");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(true);
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const run = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await profileApi.get();
        setProfile(data);
        setDisplayName(data.display_name);
      } catch (apiError) {
        setError(apiError instanceof Error ? apiError.message : "載入個人資料失敗");
      } finally {
        setLoading(false);
      }
    };

    void run();
  }, []);

  const avatarText = useMemo(() => {
    if (profile?.avatar_fallback) {
      return profile.avatar_fallback;
    }
    if (displayName.trim()) {
      return displayName.trim().slice(0, 1);
    }
    return "?";
  }, [displayName, profile?.avatar_fallback]);

  const handleSaveProfile = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = displayName.trim();
    if (!trimmed) {
      setError("使用者名稱不可為空白");
      return;
    }

    setSavingProfile(true);
    setMessage(null);
    setError(null);
    try {
      const updated = await profileApi.update({ display_name: trimmed });
      setProfile(updated);
      setDisplayName(updated.display_name);
      setMessage("個人資料已更新");
    } catch (apiError) {
      setError(apiError instanceof Error ? apiError.message : "更新個人資料失敗");
    } finally {
      setSavingProfile(false);
    }
  };

  const handleChangePassword = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!currentPassword || !newPassword || !confirmPassword) {
      setError("請完整填寫密碼欄位");
      return;
    }
    if (newPassword.length < 8) {
      setError("新密碼至少需要 8 個字元");
      return;
    }
    if (newPassword !== confirmPassword) {
      setError("確認新密碼與新密碼不一致");
      return;
    }

    setSavingPassword(true);
    setMessage(null);
    setError(null);
    try {
      await profileApi.changePassword({ current_password: currentPassword, new_password: newPassword });
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
      setMessage("密碼已更新");
    } catch (apiError) {
      setError(apiError instanceof Error ? apiError.message : "修改密碼失敗");
    } finally {
      setSavingPassword(false);
    }
  };

  if (loading) {
    return <section className="card workspace-card">載入個人資料中...</section>;
  }

  return (
    <section className="card workspace-card profile-page">
      <h2 className="workspace-title">
        <FiUser aria-hidden="true" /> 個人資料
      </h2>

      <div className="profile-avatar-row">
        <span className="profile-avatar" aria-label="預設頭像">
          {avatarText}
        </span>
        <div>
          <p className="muted-text">未上傳頭像時，使用顯示名稱第一個字元作為預設頭像。</p>
        </div>
      </div>

      <form onSubmit={handleSaveProfile} className="settings-form" noValidate>
        <label htmlFor="profile-display-name">使用者名稱</label>
        <input
          id="profile-display-name"
          value={displayName}
          onChange={(event) => setDisplayName(event.target.value)}
          maxLength={120}
          placeholder="請輸入使用者名稱"
        />

        <label htmlFor="profile-email">
          <FiMail aria-hidden="true" /> Email（不可修改）
        </label>
        <input id="profile-email" value={profile?.email ?? ""} disabled aria-disabled="true" />

        <button type="submit" className="btn" disabled={savingProfile} aria-label="儲存個人資料">
          <FiSave aria-hidden="true" /> {savingProfile ? "儲存中..." : "儲存個人資料"}
        </button>
      </form>

      <hr className="section-divider" />

      <h3 className="workspace-subtitle">
        <FiKey aria-hidden="true" /> 修改密碼
      </h3>
      <form onSubmit={handleChangePassword} className="settings-form" noValidate>
        <label htmlFor="current-password">目前密碼</label>
        <div className="password-field">
          <input
            id="current-password"
            type={showCurrentPassword ? "text" : "password"}
            value={currentPassword}
            onChange={(event) => setCurrentPassword(event.target.value)}
            placeholder="請輸入目前密碼"
          />
          <button
            type="button"
            className="btn ghost password-toggle"
            onClick={() => setShowCurrentPassword((prev) => !prev)}
            aria-label={showCurrentPassword ? "隱藏目前密碼" : "顯示目前密碼"}
          >
            {showCurrentPassword ? <FiEyeOff aria-hidden="true" /> : <FiEye aria-hidden="true" />}
          </button>
        </div>

        <label htmlFor="new-password">新密碼</label>
        <div className="password-field">
          <input
            id="new-password"
            type={showNewPassword ? "text" : "password"}
            value={newPassword}
            onChange={(event) => setNewPassword(event.target.value)}
            placeholder="至少 8 個字元"
          />
          <button
            type="button"
            className="btn ghost password-toggle"
            onClick={() => setShowNewPassword((prev) => !prev)}
            aria-label={showNewPassword ? "隱藏新密碼" : "顯示新密碼"}
          >
            {showNewPassword ? <FiEyeOff aria-hidden="true" /> : <FiEye aria-hidden="true" />}
          </button>
        </div>

        <label htmlFor="confirm-password">確認新密碼</label>
        <div className="password-field">
          <input
            id="confirm-password"
            type={showConfirmPassword ? "text" : "password"}
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
            placeholder="請再次輸入新密碼"
          />
          <button
            type="button"
            className="btn ghost password-toggle"
            onClick={() => setShowConfirmPassword((prev) => !prev)}
            aria-label={showConfirmPassword ? "隱藏確認新密碼" : "顯示確認新密碼"}
          >
            {showConfirmPassword ? <FiEyeOff aria-hidden="true" /> : <FiEye aria-hidden="true" />}
          </button>
        </div>

        <button type="submit" className="btn" disabled={savingPassword} aria-label="更新密碼">
          <FiKey aria-hidden="true" /> {savingPassword ? "更新中..." : "更新密碼"}
        </button>
      </form>

      {message ? <p className="success-text">{message}</p> : null}
      {error ? <p className="error-text">{error}</p> : null}
    </section>
  );
}
