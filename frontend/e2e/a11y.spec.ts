import AxeBuilder from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

// 可访问性门禁：用 axe-core 扫描渲染后的邀请主界面，
// 出现 serious / critical 级别的 WCAG 2.0 A/AA 违规即失败。
// 后端用 route 拦截返回空列表，使扫描不依赖真实后端。

test("邀请主界面无严重可访问性违规", async ({ page }) => {
  await page.route("**/api/tenants/**", (route) =>
    route.fulfill({ status: 200, json: [] }));
  await page.goto("/");
  await expect(page.getByRole("button").first()).toBeVisible();

  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa"])
    .analyze();

  console.log(
    `axe-core ${results.testEngine.version}: ` +
      `violations=${results.violations.length}, passes=${results.passes.length}`,
  );
  const serious = results.violations.filter(
    (v) => v.impact === "serious" || v.impact === "critical");
  expect(serious).toEqual([]); // 有严重违规即失败
});
