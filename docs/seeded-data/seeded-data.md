# Seeded Data Reference

All data loaded automatically on first `docker compose up` from `compose/init.sql`.

---

## Users

| ID | Email | Full Name | Type | Admin | Active | Plan |
|----|-------|-----------|------|-------|--------|------|
| `4c77a195-2d4a-45d5-beb0-d2479642a885` | wanawaf482@brixozu.com | m | job_seeker | No | Yes | free |
| `f4f637bb-d25f-437f-b891-f8e6d2ce3936` | m@gmail.com | iii | employer | No | Yes | free |
| `532c01cf-517b-41a7-91a9-d87d17f55b73` | carekev655@divahd.com | muq | employer | No | Yes | free |
| `4717d011-f88d-47bc-b271-65a6d7760868` | muktadasalam1111@gmail.com | n | job_seeker | No | Yes | free |
| `d9cd6f66-88a5-495d-a6b8-a27b5cea4f55` | seeker@mehna.com | علي حسين | job_seeker | No | Yes | free |
| **`e6f4709f-976e-4562-96a8-277ecb07e86e`** | **employer@mehna.com** | **أحمد محمد** | **admin** | **Yes** | **Yes** | **free** |
| `dbde562e-1829-4182-b1fe-bb00a13eb855` | bipej67781@divahd.com | q | employer | No | Yes | free |

### Super Admin Credentials

| Field | Value |
|-------|-------|
| Email | `employer@mehna.com` |
| Password | `123456` |
| Name | أحمد محمد |
| Role | admin (super admin) |

> Passwords are hashed with `scrypt`. The plaintext `123456` is used for development only.

---

## Companies

| ID | Name | Location | Verification | Documents |
|----|------|----------|-------------|-----------|
| `15b5ec56-a136-46ac-a8da-787efb80c201` | مطعم كرار بركر | النجف | verified | المالك: احمد / رقم الهوية: 567987654 |
| `b0c7dbd2-f7ad-422b-96e7-310ff2e36a29` | mgg | 444 | verified | المالك: gmg / رقم الهوية: 3432535 |

---

## Notifications

| ID | User ID | Message | Read |
|----|---------|---------|------|
| `94e652a8-6886-433e-8347-572926592395` | `4717d011-...` (muktadasalam1111@gmail.com) | تهانينا! تم قبولك في "m" | Yes |
| `c7890387-ee27-484c-a541-143d3ac82899` | `4717d011-...` | تهانينا! تم قبولك في "m" | Yes |
| `98cfc033-0baa-49e5-865f-26b6b7a74fe3` | `4717d011-...` | تهانينا! تم قبولك في "ة" | Yes |
| `3888aa70-1771-4a04-9579-3fee319b8cc3` | `4717d011-...` | تهانينا! تم قبولك في "m" | No |
| `81c433ec-2026-4268-9a1f-7dacec16fd89` | `4c77a195-...` (wanawaf482@brixozu.com) | تهانينا! تم قبولك في "m" | Yes |

---

## Profiles

| User ID | Bio | Skills | Phone | Location |
|---------|-----|--------|-------|----------|
| `4c77a195-...` (wanawaf482@brixozu.com) | — | — | — | — |
| `4717d011-...` (muktadasalam1111@gmail.com) | — | — | — | — |

---

## Jobs

No jobs seeded in the database dump.

---

## Applications

No applications seeded in the database dump.

---

## Saved Jobs

No saved jobs seeded in the database dump.

---

## Skills

No skills seeded in the database dump.
