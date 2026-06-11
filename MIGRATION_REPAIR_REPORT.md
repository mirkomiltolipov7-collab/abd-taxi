MIGRATION REPAIR REPORT

Date: 2026-06-09

Root cause
-----------
- The only existing Prisma migration in `backend/prisma/migrations` was `20250606120000_email_verification`.
- That migration assumed the `User` table already existed.
- The Railway database was empty, so the migration failed with:
  - `P3006`
  - `The underlying table for model User does not exist`
- In other words, the migration chain was incomplete: there was no base migration creating core tables before the email verification update.

Fix applied
-----------
- Created a new initial migration: `20250606110000_init`.
- This migration creates the full current schema from the empty database, including all core models and relations.
- Left `20250606120000_email_verification` in place, but replaced its SQL with a no-op comment so it can be part of the chain without reapplying invalid assumptions.
- The migration order is now:
  1. `20250606110000_init`
  2. `20250606120000_email_verification`

Verification
------------
- Ran successfully from the empty Railway database:
  - `cd backend`
  - `npx prisma migrate dev --name init`
- Prisma applied both migrations successfully.
- `npx prisma migrate status --schema prisma/schema.prisma` reports:
  - `2 migrations found in prisma/migrations`
  - `Database schema is up to date!`
- `npx prisma generate` also ran successfully.
- `npm run build` also ran successfully.

Tables created
--------------
The repaired initial migration creates the following core tables (among others):
- `User`
- `Driver`
- `Order`
- `RefreshToken`
- `EmailVerification`
- `SmsOtp`
- `Vehicle`
- `OrderStatusHistory`
- `Payment`
- `Review`
- `DriverTrustScore`
- `DriverMetrics`
- `DriverLocationHistory`
- `OrderChatMessage`
- `OrderPhoto`
- `Address`
- `SupportTicket`
- `SupportMessage`
- `EmailOtp`

Migration status
----------------
- `backend/prisma/migrations/20250606110000_init` - applied
- `backend/prisma/migrations/20250606120000_email_verification` - applied
- Database schema is in sync with `backend/prisma/schema.prisma`.

Next step
---------
- At this stage the Prisma migration issue is repaired.
- The next manual step is to run the backend and perform the requested end-to-end tests for:
  - Email OTP
  - Photo upload
  - Address book
  - Support tickets

Note
----
- No new application features were implemented.
- Only Prisma migration repair was performed until `npx prisma migrate dev` succeeded.
