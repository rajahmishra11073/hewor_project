# Hewor Agency & Tools - Project Documentation

## 1. Project Overview
**Hewor Agency** is a dual-purpose web platform:
1.  **Academic & Digital Services Agency:** Connecting clients with expert freelancers for services like Thesis Creation, PPT Making, Data Entry, and Consultation.
2.  **Free PDF Tools Suite:** A collection of 20+ powerful online PDF utilities (Merge, Split, Convert, Compress) similar to iLovePDF/SmallPDF.

The platform includes a robust **Freelancer Management System** where admins assign work, and freelancers view/accept orders via a real-time dashboard.

---

## 2. Technology Stack
*   **Framework:** Django 5.2 (Python)
*   **Database:** 
    *   **Development:** SQLite
    *   **Production:** MySQL (via Railway / `dj_database_url`)
*   **Frontend:**
    *   **Styling:** TailwindCSS (via CDN) + Custom CSS (`index.css`)
    *   **Interactivity:** Alpine.js (for reactive UI components)
    *   **Dynamic UX:** HTMX (for real-time dashboard polling and swapping)
*   **Authentication:** 
    *   Django Auth System
    *   Google Firebase Auth (Integrated for Social Login)
*   **PDF Processing:** `PyMuPDF` (fitz), `pdfplumber`, `reportlab`, `python-docx`, `openpyxl`, `python-pptx`.
*   **Deployment:** Railway (Production-ready with Whitenoise).

---

## 3. Core Applications & Features

### A. Client Portal (User Side)
*   **Service Ordering:** Users can book services (Presentation, Typing, etc.) and upload requirement files.
*   **Order Tracking:** Dashboard showing order status (Pending → In Progress → Delivered).
*   **Chat System:** Direct chat with Admin regarding specific orders (`OrderChat`).
*   **File Management:** Download delivered files and upload additional source files.
*   **Payments:** Manual payment verification flow (Upload Screenshot + Transaction ID).

### B. PDF Tools Suite (20+ Tools)
Fully functional tools available at `/tools/`:
1.  **Organization:** Merge PDF, Split PDF, Remove Pages, Extract Pages, Organize PDF.
2.  **Optimization:** Compress PDF (Ghostscript/pypdf optimizations).
3.  **Conversion (To PDF):** Word to PDF, Excel to PDF, PPT to PDF, JPG to PDF, HTML to PDF.
4.  **Conversion (From PDF):** PDF to Word, PDF to Excel, PDF to PPT, PDF to JPG.
5.  **Security:** Protect PDF (Password), Unlock PDF, Sign PDF (Digital Signature).
6.  **Editing:** Add Page Numbers, Add Watermark, Rotate PDF.
7.  **Creative:** Whiteboard (Draw and save as PDF).

### C. Freelancer Portal (`/freelancer/`)
*   **Dedicated Dashboard:** Real-time view of assigned orders.
*   **Job Bidding:** View "Pending Acceptance" orders with price and deadline.
*   **Accept/Reject Flow:** Freelancers can accept or reject assignments.
*   **Real-time Alerts:** Dashboard auto-refreshes (HTMX) every 5s; Pending orders have a visual "Ring" alert.
*   **Earnings Tracker:** Track weekly/monthly/total earnings in `₹`.
*   **Rating System:** Freelancer performance ratings.

### D. Admin Control Panel (Custom + Jazzmin)
*   **Order Panel:** Custom dashboard for Admins (`/order-panel/`) to manage orders, assign freelancers, and mark payments.
*   **Freelancer Management:** View profiles, hire/fire, send notifications.
*   **Notification System:** Broadcast messages to all freelancers.

---

## 4. Database Models (`core/models.py`)

| Model | Description |
|-------|-------------|
| `Profile` | Extends user with phone number and profile pic. |
| `ServiceOrder` | The core entity. Tracks client, service type, files, payment, status. Links to `Freelancer`. |
| `OrderFile` | Files attached to an order (Source vs. Delivery). |
| `Freelancer` | Freelancer profile, expertise, rating, QR code for payments. |
| `OrderChat` | Chat messages between Client and Admin. |
| `FreelancerChat`| Chat messages between Freelancer and Admin. |
| `Review` | Client testimonials displayed on Home. |
| `CaseStudy` | Success stories displayed on "Case Studies" page. |
| `BlogPost` | SEO content model with Categories and Tags. |
| `SiteSetting` | Dynamic configuration for Contact Info, About Text, etc. |

---

## 5. Key Workflows

### 1. New Service Order Flow
1.  User clicks "Get Started" or "Order Now".
2.  Fills form (Service Type, Title, Description, File Upload).
3.  Redirected to Payment Page (Manual UPI flow).
4.  Admin verifies payment -> Status "In Progress".
5.  Admin assigns to Freelancer via Order Panel.

### 2. Freelancer Assignment Flow
1.  Admin selects a freelancer for an Order.
2.  Order appears on Freelancer Dashboard as "Pending Acceptance".
3.  Freelancer sees Price and Deadline.
4.  Freelancer clicks **Accept** -> Status "Accepted".
5.  Freelancer downloads files, completes work.
6.  Freelancer uploads work via "Submit Work" button.

### 3. PDF Tool Flow
1.  User selects tool (e.g., PDF to Word).
2.  Uploads PDF.
3.  Server processes file (using `core/utils_pdf.py`).
4.  File is saved to `media/temp/`.
5.  User is redirected to **Download Page**.
6.  Auto-cleanup deletes files after usage.

---

## 6. Recent Optimizations & Fixes
*   **Speed:** Homepage is cached (`@cache_page(15mins)`). Database queries logic optimized.
*   **SEO:** 
    *   Dynamic `sitemap.xml` generated automatically.
    *   `robots.txt` configured to allow indexing.
    *   Meta tags and semantic HTML implemented.
*   **Real-Time UI:** Freelancer Dashboard uses HTMX to poll for new orders without page reloads.
*   **Bug Fixes:** 
    *   Fixed PDF-to-Word conversion logic.
    *   Fixed Freelancer Price Display syntax errors.
    *   Fixed Dashboard "Alert Ring" visual bugs.
    *   Fixed "Add Freelancer" JS modal issues.

---

## 7. Deployment & Environment
To run this project:

1.  **Install Requirements:** `pip install -r requirements.txt`
2.  **Environment Variables (`.env`):**
    *   `SECRET_KEY`, `DEBUG`
    *   `DATABASE_URL` (for MySQL)
    *   `FIREBASE_ADMIN_CREDENTIALS` (for Auth)
3.  **Run Migrations:** `python manage.py migrate`
4.  **Start Server:** `python manage.py runserver`

**Production (Railway):**
*   Uses `whitenoise` for static files.
*   Uses `gunicorn` as WSGI server.
*   `Procfile` handles startup.

---

*Generated by Antigravity AI Assistant for Rajesh Kumar Mishra.*
