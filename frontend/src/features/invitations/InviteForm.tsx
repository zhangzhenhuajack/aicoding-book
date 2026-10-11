import { useState } from "react";

import { ApiError, createInvitation, type Role } from "./api";

interface Props {
  tenantId: string;
  demoUser: string;
}

export function InviteForm({ tenantId, demoUser }: Props) {
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<Role>("member");
  const [token, setToken] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setToken(null);
    try {
      const created = await createInvitation(tenantId, demoUser, { email, role });
      setToken(created.token);
      setEmail("");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "创建邀请失败");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form onSubmit={onSubmit} aria-label="创建邀请">
      <div>
        <label htmlFor="invite-email">邮箱</label>
        <input
          id="invite-email"
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </div>
      <div>
        <label htmlFor="invite-role">角色</label>
        <select
          id="invite-role"
          value={role}
          onChange={(e) => setRole(e.target.value as Role)}
        >
          <option value="member">member</option>
          <option value="admin">admin</option>
        </select>
      </div>
      <button type="submit" disabled={busy}>
        发送邀请
      </button>
      {token && (
        <p role="status">
          一次性邀请 token（仅显示一次）：<code>{token}</code>
        </p>
      )}
      {error && <p role="alert">{error}</p>}
    </form>
  );
}
