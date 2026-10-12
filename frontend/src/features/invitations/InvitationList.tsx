import { useEffect, useState } from "react";

import {
  ApiError,
  type Invitation,
  listInvitations,
  revokeInvitation,
} from "./api";

interface Props {
  tenantId: string;
  demoUser: string;
}

export function InvitationList({ tenantId, demoUser }: Props) {
  const [rows, setRows] = useState<Invitation[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      setRows(await listInvitations(tenantId, demoUser, "pending"));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "加载失败");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [tenantId, demoUser]);

  async function onRevoke(id: string) {
    try {
      await revokeInvitation(tenantId, demoUser, id);
      await refresh();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "撤销失败");
    }
  }

  if (loading) return <p>加载中…</p>;

  return (
    <section aria-label="待处理邀请">
      <h2>待处理邀请</h2>
      {error && <p role="alert">{error}</p>}
      {rows.length === 0 ? (
        <p>暂无待处理邀请</p>
      ) : (
        <ul>
          {rows.map((inv) => (
            <li key={inv.id}>
              <span>
                {inv.email}（{inv.role}）
              </span>
              <button
                type="button"
                aria-label={`撤销 ${inv.email} 的邀请`}
                onClick={() => void onRevoke(inv.id)}
              >
                撤销
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
