# bui-reporting
Add readme info...

## Security Notice

**IMPORTANT**: This repository previously had a .env file with sensitive credentials committed to git history. The following actions have been taken:

1. ✅ Removed .env file from git tracking
2. ✅ Updated .gitignore to properly exclude .env files  
3. ✅ Created .env.example template for setup

**REQUIRED ACTION**: The following credentials that were exposed need to be rotated immediately:
- Database password for user `AppUser` 
- Email password for `no-reply@toyotatz.com`

## Setup

1. Copy `.env.example` to `.env`
2. Update `.env` with your actual credentials
3. Ensure `.env` is never committed to git

<!-- Security scan triggered at 2025-09-01 23:19:59 -->

<!-- Security scan triggered at 2025-09-07 01:47:57 -->