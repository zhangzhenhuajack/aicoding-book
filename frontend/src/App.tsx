import { AcceptInvitePage } from "./features/invitations/AcceptInvitePage";
import { InvitationList } from "./features/invitations/InvitationList";
import { InviteForm } from "./features/invitations/InviteForm";

// 演示用固定租户与登录用户（生产由 OIDC/JWT 决定）。
const DEMO_TENANT = "00000000-0000-0000-0000-000000000001";
const DEMO_USER = "owner@acme.example.com";

export function App() {
  return (
    <main>
      <h1>TeamPulse 邀请</h1>
      <InviteForm tenantId={DEMO_TENANT} demoUser={DEMO_USER} />
      <InvitationList tenantId={DEMO_TENANT} demoUser={DEMO_USER} />
      <hr />
      <AcceptInvitePage demoUser="invitee@acme.example.com" />
    </main>
  );
}
