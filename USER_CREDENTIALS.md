# HRMS Portal - User Credentials

**Created:** February 12, 2026  
**Total Users:** 5

---

## Login Credentials

### 1. Admin User
- **Username:** `deep`
- **Email:** deep@clouddownunder.com.au
- **Password:** `deep@123`
- **Role:** Admin
- **Permissions:** Full system access

### 2. HR User
- **Username:** `arfin.kazi`
- **Email:** arfin.kazi@trilokninfotech.com
- **Password:** `arfin.kazi@123`
- **Role:** HR
- **Department:** Human Resources
- **Permissions:** Employee management, recruitment, leave management

### 3. Manager User
- **Username:** `pratik`
- **Email:** pratik@clouddownunder.com.au
- **Password:** `pratik@123`
- **Role:** Manager
- **Permissions:** Team management, leave approvals

### 4. IT Admin User
- **Username:** `yuvraj.shinde`
- **Email:** yuvraj.shinde@trilokninfotech.com
- **Password:** `yuvraj.shinde@123`
- **Role:** IT Admin
- **Department:** IT Department
- **Permissions:** System settings, device management

### 5. Employee User
- **Username:** `vijay.bhesaniya`
- **Email:** vijay.bhesaniya@trilokninfotech.com
- **Password:** `vijay.bhesaniya@123`
- **Role:** Employee
- **Department:** IT Department
- **Permissions:** View own profile, apply for leave

---

## Important Notes

⚠️ **SECURITY REMINDERS:**
1. All users should change their passwords after first login
2. Keep this document secure and do not share publicly
3. Delete this file after distributing credentials to users
4. Use strong passwords for production environments

## Login URL
- Local: http://localhost:8000/accounts/login/
- Production: [Your production URL]/accounts/login/

## Password Reset
If users forget their passwords, admin can reset them via:
1. Django Admin: `/admin/`
2. Management command: `python manage.py changepassword username`

## Adding More Users
To add more users, use the Django admin interface or create them programmatically.

---

**Document Status:** Active  
**Last Updated:** February 12, 2026
