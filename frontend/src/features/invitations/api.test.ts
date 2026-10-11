import { afterEach, describe, expect, it, vi } from "vitest";

import { acceptInvitation, ApiError, createInvitation } from "./api";

function mockFetch(status: number, body: unknown) {
  return vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response);
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("api client", () => {
  it("createInvitation 成功返回含一次性 token 的对象", async () => {
    const payload = {
      id: "i1",
      tenant_id: "t1",
      email: "a@acme.example.com",
      role: "member",
      status: "pending",
      expires_at: "2026-10-15T00:00:00Z",
      created_at: "2026-10-08T00:00:00Z",
      accepted_at: null,
      token: "plain-token-123",
    };
    vi.stubGlobal("fetch", mockFetch(201, payload));

    const created = await createInvitation("t1", "owner@acme.example.com", {
      email: "a@acme.example.com",
      role: "member",
    });
    expect(created.token).toBe("plain-token-123");
    expect(created.status).toBe("pending");
  });

  it("错误体被转成 ApiError，带 code 与 httpStatus", async () => {
    vi.stubGlobal(
      "fetch",
      mockFetch(410, { error: { code: "INVITATION_EXPIRED", message: "邀请已过期" } }),
    );
    await expect(
      acceptInvitation("invitee@acme.example.com", "tok"),
    ).rejects.toMatchObject({
      name: "ApiError",
      code: "INVITATION_EXPIRED",
      httpStatus: 410,
    });
  });

  it("发送请求时带 X-Demo-User 头", async () => {
    const spy = mockFetch(201, {
      id: "i",
      tenant_id: "t",
      email: "a@acme.example.com",
      role: "member",
      status: "pending",
      expires_at: "x",
      created_at: "y",
      accepted_at: null,
      token: "t",
    });
    vi.stubGlobal("fetch", spy);
    await createInvitation("t1", "owner@acme.example.com", {
      email: "a@acme.example.com",
      role: "member",
    });
    const init = spy.mock.calls[0]?.[1] as RequestInit;
    const headers = init.headers as Record<string, string>;
    expect(headers["X-Demo-User"]).toBe("owner@acme.example.com");
  });

  it("ApiError 是 Error 的子类", () => {
    const e = new ApiError("X", "msg", 400);
    expect(e).toBeInstanceOf(Error);
  });
});
