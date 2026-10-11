import { expect, test } from "@playwright/test";

// E2E 覆盖关键路径：创建邀请 → 出现在列表 → 撤销。
// 后端用 Playwright 的 route 拦截 mock，使 E2E 不依赖真实后端即可跑通关键 UI 流程。
// 若对接真实后端，去掉 route mock、让 webServer 同时起后端即可。

const TENANT = "00000000-0000-0000-0000-000000000001";

test("创建邀请 → 列表出现 → 撤销", async ({ page }) => {
  const pending: Array<{ id: string; email: string; role: string }> = [];

  await page.route("**/api/tenants/**", async (route) => {
    const req = route.request();
    const url = req.url();
    if (req.method() === "POST" && url.includes("/revoke")) {
      const id = url.split("/invitations/")[1]!.split("/revoke")[0]!;
      const idx = pending.findIndex((p) => p.id === id);
      if (idx >= 0) pending.splice(idx, 1);
      await route.fulfill({ status: 200, json: { id, status: "revoked" } });
      return;
    }
    if (req.method() === "POST") {
      const body = req.postDataJSON() as { email: string; role: string };
      const inv = { id: `inv-${pending.length + 1}`, email: body.email, role: body.role };
      pending.push(inv);
      await route.fulfill({
        status: 201,
        json: {
          ...inv,
          tenant_id: TENANT,
          status: "pending",
          expires_at: "2026-10-15T00:00:00Z",
          created_at: "2026-10-08T00:00:00Z",
          accepted_at: null,
          token: "e2e-one-time-token",
        },
      });
      return;
    }
    // GET 列表
    await route.fulfill({
      status: 200,
      json: pending.map((p) => ({
        ...p,
        tenant_id: TENANT,
        status: "pending",
        expires_at: "2026-10-15T00:00:00Z",
        created_at: "2026-10-08T00:00:00Z",
        accepted_at: null,
      })),
    });
  });

  await page.goto("/");

  // 创建邀请
  await page.getByLabel("邮箱").fill("e2e@acme.example.com");
  await page.getByRole("button", { name: "发送邀请" }).click();
  await expect(page.getByText("e2e-one-time-token")).toBeVisible();

  // 列表出现该邀请（刷新一次页面触发列表重新拉取）
  await page.reload();
  await expect(page.getByText(/e2e@acme.example.com/)).toBeVisible();

  // 撤销
  await page.getByRole("button", { name: /撤销 e2e@acme.example.com/ }).click();
  await expect(page.getByText("暂无待处理邀请")).toBeVisible();
});
