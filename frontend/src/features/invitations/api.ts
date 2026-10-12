// 邀请功能的 API 客户端。封装 fetch，统一带 X-Demo-User 头（演示登录），
// 并把后端的统一错误体 {error:{code,message}} 转成前端可处理的 ApiError。

export type Role = "admin" | "member";
export type InvitationStatus = "pending" | "accepted" | "revoked" | "expired";

export interface Invitation {
  id: string;
  tenant_id: string;
  email: string;
  role: Role;
  status: InvitationStatus;
  expires_at: string;
  created_at: string;
  accepted_at: string | null;
}

export interface InvitationCreated extends Invitation {
  token: string; // 一次性明文 token，仅创建响应返回一次
}

export interface AcceptResult {
  tenant_id: string;
  user_email: string;
  role: Role;
  status: InvitationStatus;
}

export class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
    public httpStatus: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

const BASE = (import.meta.env?.VITE_API_BASE as string | undefined) ?? "";

async function request<T>(
  path: string,
  demoUser: string,
  init?: RequestInit,
): Promise<T> {
  const resp = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-Demo-User": demoUser,
      ...(init?.headers ?? {}),
    },
  });
  if (!resp.ok) {
    let code = "UNKNOWN";
    let message = `HTTP ${resp.status}`;
    try {
      const body = (await resp.json()) as { error?: { code: string; message: string } };
      if (body.error) {
        code = body.error.code;
        message = body.error.message;
      }
    } catch {
      // 非 JSON 错误体，保留默认
    }
    throw new ApiError(code, message, resp.status);
  }
  return (await resp.json()) as T;
}

export function createInvitation(
  tenantId: string,
  demoUser: string,
  body: { email: string; role: Role },
): Promise<InvitationCreated> {
  return request<InvitationCreated>(
    `/api/tenants/${tenantId}/invitations`,
    demoUser,
    { method: "POST", body: JSON.stringify(body) },
  );
}

export function listInvitations(
  tenantId: string,
  demoUser: string,
  status: InvitationStatus = "pending",
): Promise<Invitation[]> {
  return request<Invitation[]>(
    `/api/tenants/${tenantId}/invitations?status=${status}`,
    demoUser,
  );
}

export function revokeInvitation(
  tenantId: string,
  demoUser: string,
  invitationId: string,
): Promise<Invitation> {
  return request<Invitation>(
    `/api/tenants/${tenantId}/invitations/${invitationId}/revoke`,
    demoUser,
    { method: "POST" },
  );
}

export function acceptInvitation(
  demoUser: string,
  token: string,
): Promise<AcceptResult> {
  return request<AcceptResult>(`/api/invitations/accept`, demoUser, {
    method: "POST",
    body: JSON.stringify({ token }),
  });
}
