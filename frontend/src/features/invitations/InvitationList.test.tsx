import { render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { InvitationList } from "./InvitationList";

afterEach(() => vi.restoreAllMocks());

describe("InvitationList", () => {
  it("渲染 pending 邀请列表", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => [
          {
            id: "i1",
            tenant_id: "t1",
            email: "pending@acme.example.com",
            role: "member",
            status: "pending",
            expires_at: "x",
            created_at: "y",
            accepted_at: null,
          },
        ],
      } as Response),
    );

    render(<InvitationList tenantId="t1" demoUser="owner@acme.example.com" />);
    await waitFor(() =>
      expect(screen.getByText(/pending@acme.example.com/)).toBeInTheDocument(),
    );
    expect(
      screen.getByRole("button", { name: /撤销 pending@acme.example.com/ }),
    ).toBeInTheDocument();
  });

  it("空列表展示空态文案", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => [] } as Response),
    );
    render(<InvitationList tenantId="t1" demoUser="owner@acme.example.com" />);
    await waitFor(() =>
      expect(screen.getByText("暂无待处理邀请")).toBeInTheDocument(),
    );
  });
});
