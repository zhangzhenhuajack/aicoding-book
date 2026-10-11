import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { InviteForm } from "./InviteForm";

afterEach(() => vi.restoreAllMocks());

describe("InviteForm", () => {
  it("提交后展示一次性 token（用户可见行为）", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 201,
        json: async () => ({
          id: "i1",
          tenant_id: "t1",
          email: "new@acme.example.com",
          role: "member",
          status: "pending",
          expires_at: "x",
          created_at: "y",
          accepted_at: null,
          token: "e2e-one-time-token",
        }),
      } as Response),
    );

    render(<InviteForm tenantId="t1" demoUser="owner@acme.example.com" />);
    await userEvent.type(screen.getByLabelText("邮箱"), "new@acme.example.com");
    await userEvent.click(screen.getByRole("button", { name: "发送邀请" }));

    await waitFor(() =>
      expect(screen.getByText("e2e-one-time-token")).toBeInTheDocument(),
    );
  });

  it("后端返回错误时展示错误消息", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 409,
        json: async () => ({
          error: { code: "ALREADY_MEMBER", message: "该邮箱已是租户成员" },
        }),
      } as Response),
    );

    render(<InviteForm tenantId="t1" demoUser="owner@acme.example.com" />);
    await userEvent.type(screen.getByLabelText("邮箱"), "already@acme.example.com");
    await userEvent.click(screen.getByRole("button", { name: "发送邀请" }));

    await waitFor(() =>
      expect(screen.getByRole("alert")).toHaveTextContent("该邮箱已是租户成员"),
    );
  });
});
