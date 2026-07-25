# FSAD Exceptions Log

Standing rule 4 of `AGENTS.md` policy requires signed commits (GPG/SSH) where the
environment supports it. Any agent or environment that cannot sign must log the
exception here rather than silently skipping it.

---

## 2026-07-25 08:32:27 UTC — Unsigned commits (automated agent environment)

- **Scope**: Commits on branch `feat/headless-cli-tooling` and subsequent branches
  created during this automated session.
- **Reason**: No GPG secret key and no SSH signing key are provisioned in the
  execution environment. `gpg --list-secret-keys` returns an empty keyring and
  `commit.gpgsign` is `false`, so commits cannot be signed.
- **Attempted**: Verified keyring, `user.signingkey`, and `commit.gpgsign` before
  committing. No signing material available to the agent, and none can be
  generated that would be meaningful for verification (an agent-generated key is
  not attested to the repository owner).
- **Impact**: Commits are authored but unverified. Content is still gated by the
  `JAIOS Turd Eye Pipeline` CI workflow and by pull-request review.
- **Remediation**: Provision a signing key in the agent environment, or have the
  repository owner squash-merge these branches with a signed merge commit. Once a
  signing key is available, remove this entry.

---
