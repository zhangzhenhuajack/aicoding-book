import { useState } from "react";

import { AcceptResult, acceptInvitation, ApiError } from "./api";

interface Props {
  demoUser: string;
  initialToken?: string;
}

export function AcceptInvitePage({ demoUser, initialToken = "" }: Props) {
  const [token, setToken] = useState(initialToken);
  const [result, setResult] = useState<AcceptResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onAccept(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setResult(null);
    try {
      setResult(await acceptInvitation(demoUser, token));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "接受邀请失败");
    }
  }

  return (
    <form onSubmit={onAccept} aria-label="接受邀请">
      <label htmlFor="accept-token">邀请 token</label>
      <input
        id="accept-token"
        value={token}
        onChange={(e) => setToken(e.target.value)}
        required
      />
      <button type="submit">接受邀请</button>
      {result && (
        <p role="status">
          已加入租户 {result.tenant_id}，角色 {result.role}
        </p>
      )}
      {error && <p role="alert">{error}</p>}
    </form>
  );
}
