# CHANGELOG
All notable changes to this project will be documented in this file.

# **[18.0.1.0.0] - 2025-10-17** 

---

- **New email notification workflow** for *unverified* customers placing orders using **Wire Transfer** or **Pay After Delivery** payment methods.
- **Recipient configuration** under `General Settings → Pay After Delivery Notification Recipients`.
  - Supports multiple comma-separated email addresses.
- **Email template** includes:
  - Customer name
  - Order reference
  - Payment method
  - Total amount
- **One-time verification workflow**:
  - Email triggered only once per unverified customer.
  - Once “Pay After Invoice” is checked on the customer record, no further emails are sent.
  - Verified customers will not trigger notifications for future website orders.

---

# [18.0.1.0.1] - 2025-11-24

- Update changelog. 
- Correct a doc string.

---
