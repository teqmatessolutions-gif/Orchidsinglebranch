# GST Reports, COA, and Journal Setup Guide

This guide provides step-by-step instructions for setting up and using the GST Accounting and Reporting features in the Resort Management System.

## 1. Chart of Accounts (COA) Setup

The accounting system is built on a Double-Entry Ledger system. You must strictly initialize the Chart of Accounts for the system to know where to post GST and Revenue.

**Action Required:**
If you have not already run the setup script, run the following command in the `ResortApp` directory:

```bash
python setup_chart_of_accounts.py
```

This script creates the following critical Account Ledgers:

*   **Tax Ledgers**:
    *   `Input CGST`, `Input SGST`, `Input IGST` (Assets)
    *   `Output CGST`, `Output SGST`, `Output IGST` (Liabilities)
*   **Revenue Ledgers**:
    *   `Room Revenue (Taxable)`
    *   `Food Revenue (Taxable)`
    *   `Service Revenue (Taxable)`
*   **Expense Ledgers**:
    *   `Cost of Goods Sold (COGS)`
    *   `General Expense`

To Verify: Go to **Accounting > Chart of Accounts** in the dashboard and ensure these ledgers appear.

---

## 2. Setting GST Configuration (Place of Supply)

The system automatically calculates IGST (Inter-state) vs CGST/SGST (Intra-state) based on the customer's state compared to the Resort's state.

**Action Required:**
You must configure your resort's state code.

1.  Open `ResortApp/app/api/gst_reports.py`.
2.  Find **Line 53**: `RESORT_STATE_CODE = "29"`
3.  Update "29" (Karnataka) to your actual 2-digit GST State Code (e.g., "07" for Delhi, "27" for Maharashtra, "32" for Kerala).

---

## 3. Journal Entries (Automation)
The system is designed to trigger Journal Entries automatically. You generally do not need to create them manually.

*   **Checkouts**: When you complete a checkout, the system Credits Revenue & Output Tax, and Debits Cash/Bank/AR.
*   **Purchases**: When you add a purchase, the system Debits Inventory/Expense & Input Tax, and Credits Vendor/Bank.
*   **Food Orders**: When paid, posts to Food Revenue.

**To View**: Navigate to **Accounting > Journals**.

---

## 4. GST Reports Instructions

Navigate to **Accounting > GST Reports** (or Reports Module).

### **GSTR-1 (Outward Supplies)**
These reports show what you have sold (Output Tax Liability).

*   **B2B Sales Register**:
    *   **Use For**: GSTR-1 **Table 4A**.
    *   **Data**: All invoices issued to customers with a valid GSTIN.
*   **B2C Sales Register**:
    *   **Use For**: GSTR-1 **Table 5** (Large Invoices > ₹2.5L Inter-state) and **Table 7** (All other small consumer sales).
    *   **Data**: Consolidated view of sales to unregistered customers.
*   **HSN/SAC Summary**:
    *   **Use For**: GSTR-1 **Table 12**.
    *   **Data**: Summary of sales grouped by SAC Code (e.g., 9963 for Rooms, 996331 for Food).

### **GSTR-3B (Summary Return)**
This is a monthly self-declaration summary.

*   **Output Tax (Table 3.1)**:
    *   Sum the **Total Tax** figures from your **B2B Sales** and **B2C Sales** reports.
*   **Eligible ITC (Table 4)**:
    *   Use the **ITC Register** report.
    *   **Input Goods/Services**: Shows tax paid on purchases that you can claim back.
    *   **Ineligible**: Shows blocked credits (if any).

### **GSTR-2B Reconciliation**
*   **Action**: Download your GSTR-2B Excel file from the government GST Portal.
*   **Upload**: Go to the **ITC Register** section in the app and upload the file to verify if your vendors have actually filed their returns.

---

## 5. Deployment & Updates (Git Workflow)

To deploy these changes or update another machine:

**Step A: On Development Machine (Where you made changes)**
1.  Save the changes (especially the State Code in `gst_reports.py`).
2.  Push to the repository:
    ```bash
    git add .
    git commit -m "Update GST settings and reports"
    git push origin orchid_latest
    ```

**Step B: On Production/Client Machine**
1.  Pull the latest changes:
    ```bash
    cd c:\releasing\orchid  # Or your project folder
    git pull origin orchid_latest
    ```
2.  Run the setup script to ensure new ledgers are created:
    ```bash
    cd ResortApp
    python setup_chart_of_accounts.py
    ```
3.  Restart the application (Backend & Frontend) to apply changes.
