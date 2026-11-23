# Security hardening — audit notes

This project began as an early personal app (2022). Before publishing it as a
code sample it was audited and the following issues were found and fixed. The
notes are kept here deliberately, as a record of the review.

## Fixed

| # | Severity | Issue | Fix |
|---|----------|-------|-----|
| 1 | Critical | **Authentication bypass** — a Flask-Login `request_loader` accepted a raw `id` from the POST body as identity, letting anyone log in as any user. | Removed the `request_loader`; the app authenticates by session (`login_user`) only. |
| 2 | High | **CSRF** — state-changing routes were not CSRF-protected (tokens were in the templates but never validated). | Enabled `flask_wtf.csrf.CSRFProtect`; every form already renders `csrf_token`, so it is now enforced. |
| 3 | High | **Stored XSS** — message and quote bodies were rendered with `|safe` over unsanitized user HTML. | Added an `nh3` (ammonia) allowlist sanitizer applied at render (`|limpio` filter) and on store. |
| 4 | High | **IDOR** — any user could edit another user's messages (`update mensaje ... where id = %s`). | Ownership check: non-admins can only edit their own message (`and usuario_id = %s`); admin may edit any. |
| 5 | High/Med | **IDOR** — topic title/feature update had no ownership check. | Author may edit only their own topic's title; only admin can set "destacado". |
| 6 | High | **Missing authorization** — `guardar_foro`, `categorias`, `guardar_categoria` lacked the admin check that `crear_foro` had. | Centralized `es_admin()` applied to every privileged route. |
| 7 | Medium | **Weak password hashing** — `generate_password_hash(pw, "sha256")`. | Use Werkzeug's default (scrypt). |
| 8 | Medium | **HTML injection in notification emails** — user content interpolated into the HTML email body. | `markupsafe.escape` applied to the user-supplied fields. |
| 9 | Medium | **Debug mode / secrets** — `DEBUG = True`, random per-process `SECRET_KEY`, DB & SMTP credentials hardcoded. | `DEBUG` and a stable `SECRET_KEY` read from the environment; all credentials moved to environment variables (see `.env.example`). |

## Known remaining items (documented, not yet changed)

- **"Chocolate" likes (`get_choco`) hardened (fixed).** Now POST-only with a CSRF
  token (front-end AJAX updated to send it), and the server rejects likes on your
  own messages. Duplicates are prevented atomically (no check-then-insert TOCTOU)
  by `INSERT IGNORE` backed by a `UNIQUE(usuario_id, mensaje_id)` constraint.
  **Schema requirement:** add `UNIQUE KEY uq_choco (usuario_id, mensaje_id)` to
  the `chocolate` table.
- **Featured-topic flag is admin-only (fixed).** `guardar_tema` computes
  `destacado = ... and es_admin()`, so a non-admin can't feature a topic by
  posting the field.
- **Password change requires the current password (fixed).** `guardar_perfil`
  verifies the current password with `check_password_hash` before changing it.
  *Remaining:* session should be rotated on login / password change (Flask-Session
  filesystem backend needs this done explicitly).
- **Admin authorization is by role, not name (fixed).** `es_admin()` now checks
  a server-controlled `usuario.is_admin` column (fail-closed: missing/false =
  not admin). The name is identity, not authorization. This also closes the
  parser/collation differential (e.g. registering `webmaster` + a 4-byte char
  that MySQL silently truncated), reinforced by `STRICT_TRANS_TABLES` + `utf8mb4`
  on the connection. Reserved-name blocking at registration is kept as
  anti-impersonation hygiene, no longer as an authorization control.
  **Schema requirement:** `usuario` needs `is_admin TINYINT(1) NOT NULL DEFAULT 0`;
  grant admin by setting it in the database. A `UNIQUE` constraint on
  `usuario.nombre` is still recommended.
- Broad `except:` blocks remain in several handlers (legacy style).
