import { expect, test } from "@playwright/test";

// 仅用于生成书中配图：对真实构建产物截图（route mock 后端），保存到书籍 dist/img。
const OUT = "/home/ubuntu/.kiro/crew/workspace/book-v31-html/dist/img";
const TENANT = "00000000-0000-0000-0000-000000000001";

// 书中配图：窄视口 + 2 倍像素密度，只截内容区（#root），印刷时文字够大、不留大片空白。
test.use({ viewport: { width: 560, height: 640 }, deviceScaleFactor: 2 });

test("shot: 邀请主界面 + 一次性 token + 列表", async ({ page }) => {
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
          ...inv, tenant_id: TENANT, status: "pending",
          expires_at: "2026-10-15T00:00:00Z", created_at: "2026-10-08T00:00:00Z",
          accepted_at: null, token: "e2e-one-time-token",
        },
      });
      return;
    }
    await route.fulfill({
      status: 200,
      json: pending.map((p) => ({
        ...p, tenant_id: TENANT, status: "pending",
        expires_at: "2026-10-15T00:00:00Z", created_at: "2026-10-08T00:00:00Z",
        accepted_at: null,
      })),
    });
  });

  await page.goto("/");
  await page.locator("#root").screenshot({ path: `${OUT}/ch24-ui-initial.png` });

  await page.getByLabel("邮箱").fill("new@acme.example.com");
  await page.getByRole("button", { name: "发送邀请" }).click();
  await expect(page.getByText("e2e-one-time-token")).toBeVisible();
  await page.locator("#root").screenshot({ path: `${OUT}/ch24-ui-token.png` });

  await page.reload();
  await expect(page.getByText(/new@acme.example.com/)).toBeVisible();
  await page.locator("#root").screenshot({ path: `${OUT}/ch24-ui-list.png` });
});

test("shot: 错误态（已是成员 409）", async ({ page }) => {
  await page.route("**/api/tenants/**", async (route) => {
    if (route.request().method() === "POST") {
      await route.fulfill({
        status: 409,
        json: { error: { code: "ALREADY_MEMBER", message: "该邮箱已是租户成员" } },
      });
      return;
    }
    await route.fulfill({ status: 200, json: [] });
  });
  await page.goto("/");
  await page.getByLabel("邮箱").fill("already@acme.example.com");
  await page.getByRole("button", { name: "发送邀请" }).click();
  await expect(page.getByRole("alert")).toHaveText("该邮箱已是租户成员");
  await page.locator("#root").screenshot({ path: `${OUT}/ch24-ui-error.png` });
});
