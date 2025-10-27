# 💸 BudgetDesktopApp

A desktop budgeting application built with FreeSimpleGUI and SQLite3. The primary goal of this app is to help users manage their finances by tracking and setting up monthly budgets across multiple bank accounts.

---

## ✅ Features

- 📥 Add income and expenses
- 🧾 Categorize transactions (e.g., Food, Rent, Utilities)
- 📊 View budget summary and remaining balance
- 💾 Save and load transactions from a local database
- 🧠 Simple, intuitive GUI using FreeSimpleGUI
- 📆 Date-based filtering and analysis
- 📈 Visual reports (pie charts, bar graphs, scatter plots)

---

## 🚀 Getting Started

### 🧾 Download the App

Download the appropriate executable from the `dist/` folder for your system:

- **Windows**: `RatTrap.exe`
- **Linux**: `RatTrap`

### 🪙 Easy Budget Setup

1. Add a new account for each bank account you want to track.
2. Select whether each account is a **Bills** or **Spending** type.
3. Add categories specific to each account.
4. Switch to the **Transactions** window.
5. Enter the **initial deposit** to reflect each account's current balance.
6. From there, track each transaction as it occurs.

#### 💡 Budgeting Tips
- Never budget more than you currently have.
- Never budget less than what you spent.
- Always categorize your expenses.

---

## 🧭 App Walkthrough

### 🔄 POV (Point of View)
Select a month from the dropdown to view or plan financial activity for past or future dates.

### 🧾 Menu Options

#### `New`
Create:
- Spending, Bills, Savings, Loan, and Asset accounts
- Categories for Spending and Bills accounts

#### `Views`
Switch between views:
- Home/Budget
- Transactions
- Savings
- Assets/Loans
- Visualizations

---

### 💼 Accounts

Accounts are organized by type:

- **Income**
- **Spending**
- **Bills**
- **Savings**
- **Assets**
- **Loans**

---

### 🗂️ Categories

Categories are used within Spending and Bills accounts to organize and control budgets.

---

### 🏠 Budget Window

- Manage **Income**, **Spending**, and **Bills** accounts
- Transfer funds between accounts by clicking an account
- Set and update budgets per category on a monthly basis

---

### 🧾 Transactions Window

- View and manage all transactions
- See complete transaction history across accounts

---

### 💰 Savings Window

- View and track all Savings accounts
- Monitor changes on a month-to-month basis

---

### 🏦 Assets & Loans Window

- Calculate the present worth of assets
- Estimate monthly loan payments

---

### 📊 Visual Reports

Includes:
- Pie charts
- Bar graphs
- Scatter plots

Useful for visualizing category spending, account balances, and trends.

## Developers
### Setup 
```bash
git clone https://github.com/rlarabel/BudgetDesktopApp.git
cd budgetDesktopApp
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python RatTrap.py.py
```
### Create executable file of RatTrap.py
```bash
pyinstaller -wF RatTrap.py
```
### Data Storage
Uses sqlite3 for persistent storage
file location
- home/AppData/Local/RatTrap/app.db

### Git workflow
Branch -> Code Changes -> Format -> Test -> Commit -> Push -> Pull -> Check -> Merge 

### Testing
N/A

### Project Structure
- dist
  - RatTrap   # Linux App
  - RatTrap.exe   # Windows App
- events
  - files that handle user envoked event in the GUI 
- logic
  - files to create, edit, and update accounts and categories
  - sheets
    - Logic to make the tables displayed
  - visualize_data.py 
    -Scripts to create visual graphs and charts
- models
  - pov.py
    - Handles what monthly data is displayed to the user.
  - ui_cintroller.py
    - Classes that control the windows available to the user
- storage
  - init_db.py
    - Initializes the sqlite3 database
  - make_db.py
    - creates database tables if they don't already exist. 
- views
  - files to create the windows avaible to the user
- .gitignore
- example_transaction.csv
- LICENSE
- RatTrap.py  # Main file
- requirement.txt
- test_userinpit.py

### RoadMap
- Build test and fix errors
- Add Pull to git workflow
- Set up test enviorment on GitHub
- Add estimated net worth
- Add archive for accounts and categories
- Add transaction filter
  - Select a certain account and/or category 
  - Search notes or name
  - Show Transfers
  - Potenial transfer finder
  - ascending and descening prices
- Retirement planner
- Auto record bank transactions
- Track loans and assets on a month-to-month basis

### Credits
- FreeSimpleGUI
- Budgeting inspiration from YNAB