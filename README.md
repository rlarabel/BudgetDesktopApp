# BudgetDesktopApp
This desktop application was built with pysimplegui and sqlite3. The main purpose of this app
is to track and set up budgets for the user's account(s) on a monthly basis.
## Step by step guide
### Setting up
#### Getting the app 
- There is a link for a windows download in my project description and my source code is also available on GitHub.
#### Adding data for funds
- First, use the menu bar to change views to the transactions window.
- Using the New Transaction button
- Enter the inital amount, at the time, of every accounts that holds value and is worth keeping track of.
- After, head back to the account window, and the 'Funds Available' will be updated
### Set up Accounts & Categories
#### Creating accounts
- Click 'New' on the menu bar, then click on add account. 
- Make an account for every account that is being tracked. 
- Each account should be given a unique name.
- Select the account type
#### Budgeting Type
- Breaks into sub-categories.
- Ability to set a budget for each category
- Tracks funds for each category
- Commonly used for account that money is being spent like a checkings
#### Tracking Type
- No categories only the account
- Main purpose is to track the amount of funds that the user put in
- Example of this would be any investing accounts, assets, etc
#### Creating categories 
- Click 'New' on the menu bar, then click on add category.
- Select the corresponding budgeting account for the category.
- Then use a unique name to create the category
### Move Funds to an Account
#### Tracking Funds
- Using the 'Track Funds' button
- Only for tracking accounts
- Now the user should have an account and an initial amount transaction for the corresponding account
- Move all of the transaction amount to the appropriate account
#### Budgeting Funds
- Using the 'Budget Funds' button
- Only for budgeting accounts
- Now the user should have an account and an initial amount transaction for the corresponding account
- Split the transaction amount bewteen the appropriate account's categories
#### Changing the view date
- Will allow the user to budget or track funds for a future date
- Future funds are off limits to the current date that the user view
- Can always unbudget future funds, if not yet spent
- Can not go to past dates, any mistakes or savings from the past will rollover to the current month
### Checking
#### Double check the account table
- After allocating all your available money, the column 'total funds' on the bottom table should match for each account.
### After Being Set up
#### Always Keeping up
- Every new real transaction should also be created and stored in the transaction window income or outcome.
- Available Funds should be at 0 to maximize the user value on their money 
-'total funds' for a BUDGET account should always match the real total of that account
#### First spending transaction
- Click on 'New Transaction'
- Select Outcome and a categories to link the spending to
- Tracking accounts can not linked to a spending transaction
#### Tracking account options
- Money can be moved out of an account, but can't be linked to a spending transaction
- If the account loses/gain value click on the account to edit the total
- If the real account/asset is being closed/sold, update the total and close the account.
- Closing an account will return the funds the user had in it and create a transaction of the totaled difference
#### Reseting budget/goal/total:
- Enter '-' will reset these helper to not having effect the program
## Output
### Account Window
#### View Date
- Verifies the date being work on
#### Funds Available
- This represent how much money is available to the user that is not already spent or being already tracked by an account
### Budgeting Table
#### Monthly Budget
- Is the amount of money that has been added to that category in the month being viewed
#### Total available 
- Is the amount of money the user has available to spend from the viewed month's budget and all the past month's budget
### Account Table
#### Total Funds
- This represent the total amount of the user actual money.
- Budgeting accounts should display their account totals (real total)
- Tracking accounts should display the total amount that the user funded to that account
## Known Error
- The goal tracker is not completely functional
