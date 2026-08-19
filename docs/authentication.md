# Authentication and delegated access

All three surfaces operate as a signed-in user and use the same published WorkIQ resource and
delegated scope. Protocol choice changes token acquisition and presentation, not the Microsoft 365
authorization boundary.

```text
Resource  api://workiq.svc.cloud.microsoft
Scope     api://workiq.svc.cloud.microsoft/WorkIQAgent.Ask
```

The resource is the token audience; the scope is the delegated permission. Check them separately
when diagnosing authorization failures. `WorkIQAgent.Ask` requires admin consent and has no
published application-permission equivalent. Consent permits the WorkIQ call, but user ACLs and
tenant, path, method, and workload policy still decide what that call may do.

## Effective access

<figure class="workiq-diagram workiq-diagram--raster">
    <img src="../assets/images/effective-access.png" width="2582" height="1016" alt="Delegated grant, user Microsoft 365 ACLs, tenant policy, and workload controls converge on effective access, which produces a permission-trimmed result.">
</figure>

A delegated grant cannot elevate the user beyond their Microsoft 365 access. Licensing,
sensitivity labels, information barriers, and workload policy still apply.

## Client patterns

| Topology | Flow | Token presenter |
| --- | --- | --- |
| MCP over local stdio | WorkIQ CLI interactive auth | WorkIQ child process |
| Remote MCP | OAuth discovery + PKCE or OBO | MCP client |
| Local A2A or REST | Public client + authorization code with PKCE | Caller |
| Hosted A2A or REST | Confidential backend + OBO | Backend |

Proof Key for Code Exchange (PKCE) protects the authorization-code flow for clients that cannot
hold a secret. OAuth On-Behalf-Of (OBO) lets a hosted backend exchange the signed-in user's token for
a delegated WorkIQ token without changing the represented user.

### Public client

Use authorization code with PKCE through the system browser or broker. A CLI is a public client and
must not contain a client secret. Cache tokens through the identity library and key state by tenant
and user.

### Hosted backend

Use OBO to exchange a user token issued for the backend API for a delegated WorkIQ token. The
backend authenticates with a certificate, federated credential, or secret; the downstream token
still represents the user.

### Local MCP

This project starts `npx -y @microsoft/workiq mcp` over stdio. The child owns sign-in, token caching,
refresh, and reauthentication. Python controls which discovered tools reach the model but does not
handle the WorkIQ bearer token.

For remote MCP, discover authorization from the protected-resource and authorization-server
metadata instead of hard-coding an OAuth server or assuming consent authorizes every path or method.

## Security invariants

- Scope conversation, context, and task IDs by tenant, user, and their owning chat, thread, or
    workflow.
- Treat IDs as routing state, never authorization.
- Keep tokens, tool payloads, grounded text, and unrestricted reference URLs out of logs.
- Require a fresh authorized call whenever state is reused.
- Gate MCP mutations with both tenant policy and local user confirmation.

## Fast diagnosis

| Symptom | Check first |
| --- | --- |
| `401` | Audience, issuer, expiry, tenant, and client ID |
| Consent failure | Admin consent for the exact registration and scope |
| `403` | Scope, user ACL, tenant policy, license, and workload restrictions |
| Empty result | User access to the source in Microsoft 365 |
| MCP read succeeds, mutation fails | Path/method policy and local allowlist |
| Stored ID fails | Current authorization, identity ownership, then retention |
