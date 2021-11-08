# HOWTO: Downgrade from nYNAB to YNAB4

This page explains how to move from nYNAB to YNAB4 while retaining as much information as possible. See [Appendix
1](#appendix-1-ynab-4) for reasons and how to get YNAB4 running.

You will *export* your current nYNAB budget, then perform some scripted steps on the exported data, and then gradually
import it into a new YNAB4 budget. The scripted steps assume that you have Python 3 installed know how to use it. (If 
anybody wants to improve this guide with setup instructions, PRs are welcome!)

Sadly, there is not much scripted at the moment – you will spend time on manual tasks. But at least, this page supplies
a guide for handling this stuff a bit better.

## Caveats

Don't expect an automated and smooth process – this repo is more of a guide with two helper scripts. If things go wrong,
you can always delete your YNAB4 data and start again. Since we're starting with a new YNAB4 budget, nothing will be
lost.

Split transactions won't be imported as splits, but rather as individual transactions. The memo field will say "Split
1/n" though, so you'll still see which transactions belonged together.

I also don't use many YNAB features including loans and separate credit card accounts, so the import might not work
correctly for them. Please open PRs with updates if you find required changes, or comment on the main issue if it worked
for you with a specific scenario, so others will know what works and what doesn't!

## Preliminaries

**In nYNAB:** Check if any of your category names contain a : or a `, as those are not valid characters in YNAB 4.
Change these category names now. Also unhide all of your previously hidden categories, as
the import will otherwise not work for them, and you'll have to re-categorise them manually. (Not a big deal because
they will be easy to filter for, but annoying regardless).

**In nYNAB:** Export your nYNAB budget by clicking on the budget name in the upper right hand corner → Export Budget.
Download the resulting zip file (once your browser has stopped freezing if your budget is a bit older), and extract the
zip archive. It contains two files: `Budgetname as of date - Budget.csv` and `Budgetname as of date - Register.csv`.
I'll refer to these as `Budget.csv` and `Register.csv` from here on out.
   
**In YNAB4:** Install YNAB 4 (see [Appendix 1](#appendix-1-ynab-4)) and set up a new budget. Set the directory to some
place that works well for you (some location you will backup or sync, for example) in the File → Preferences dialog.  Go
to the directory you selected: You will find a directory called `My Budget~number.ynab4`.  Inside, there is a
`data1~number` directory, and inside that, there is a directory that is just one long UID, looking like
`98C499B4-4B29-6CC5-3B7A-F0247E9E2551`. Open this directory – it will contain a `budgetSettings.ybsettings` file and a
`Budget.yfull` file. I will call this directory "YNAB4 data directory" from here on out.

## Step 1: Creating accounts

As a first step, create all your accounts in YNAB 4. Please make sure they are spelt *exactly* like in nYNAB.
**Take care to also create closed accounts!**

*(It's probably not worth to automate this step, especially since the nYNAB export does not contain account information
like the account type, so even if we write an importer, we'd still have to manually correct the account type, and people
usually have a limited amount of accounts.)*

Now's a good time to make a backup of your YNAB4 data directory, because if something down the line fails, you won't
want to go through this a second time.

## Step 2: Creating categories

While accounts are limited in number, categories can be a lot, so I wrote a tiny importer. Make sure to close YNAB 4
before running it – it overrides the data file on closing!

```bash
python create_categories.py path/to/Budget.csv path/to/ynab4_data_directory
```

## Step 3: Splitting the payment export file


Now run the second split to take apart the transaction export – YNAB 4 can only import on a per-account basis.

```bash
python split_export.py path/to/nynab_data_directory/Register.csv
```

This will place one CSV file for each account in your working directory, and will replace some terms to make successful
imports more likely.

## Step 4: Importing files

You'll want to import every file next, each under the appropriate account. Make sure to select Year/Month/Date as time
format, as well as "Include transactions before account start date".

Next, approve all transactions and recategorise if any did not receive a matching category on import. This shouldn't
happen, but probably will in some edge cases. If YNAB can't find a category, it should put the category in the memo
field, so that in most cases, you can search for that field, bulk-select and handle the transactions fairly quickly.

And now the
tedious part: When you transferred money from account A to B, this transaction shows up in the account A export and the
account B export – but since YNAB 4 does not know that we'll provide both imports, it also auto generates the matching
transfer transaction, so every transfer exists twice. You have to go through the list of all transactions, filter for
Transfer, and delete every other one :/

To do this, first filter by "Is: Cleared,  Transfer". Then, the easiest workflow is to mark the first transaction, then
hold Ctrl, and keep pressing down, down, space. Delete either all the inflows or outflows – it doesn't matter, as their
counterparts will also disappear.

For context: I used nYNAB for just over five years, and I had to mark around 150 transactions. Not great, but not
terrible, either.

## Step 5: Cleanup

Now, chances are, some accounts won't have the correct balance. I'm not quite sure what's going on, to be quite honest.
Out of my 7 accounts, 2 were off (one by a bit, one by a bit more), the other five came out correct. Things to check:

- An imported starting balance can be marked incorrectly, either change the flow direction or delete it.
- Mark a suspect time period (first and last month / year / quarter) in both nYNAB and YNAB 4 and compare the totals.

Now, once all the account totals are correct: **you can be done**. Just copy your current category bucket total into
your YNAB 4, and you're ready to go. Congratulations!

## Step 6: Budget import (optional)

Unless you want your budget history to be imported, too – do you want to know how much money you set aside for vacation
in 2017? … If so: **quit YNAB 4 and make a backup of the directory**! Seriously: Your current state is very good and
you really don't want to repeat the work you just did if the budget import screws up somehow.

Then run:

```bash
python import_budgets.py path/to/Budget.csv path/to/ynab4_data_directory
```

All your budget data should get imported. Please let me know if this doesn't work – I'm assuming currencies with a
single symbol and two decimal places, for example, because I'm lazy like that. You might also try entering a random
number into your first month (e.g. April 2016) in YNAB 4 if the import fails – this will cause YNAB to create all the
monthly buckets, so that the importer only has to add the correct numbers.

When you open YNAB 4, the total budgeted numbers per category should be correct – if you use future budgeting a lot, it
might look off at first, because you'll have large visible numbers as "not budgeted". These numbers are correct though,
and should line up with what you see in the breakdown when you click the month's total in nYNAB.

## Appendix 1: YNAB 4

YNAB 4 is a desktop application that was the predecessor of the web version, commonly called nYNAB (or just YNAB). YNAB
4 did not have a subscription model, but can't be purchased anymore. If you bought it back in the day, you can still use
your activation key. You might also have bought it on Steam, where it will still be activated for you.

If you *didn't* purchase YNAB 4, you can still download it and run through the 1-month trial. There are trivial ways to
extend or repeat or circumvent the trial duration, however, as those are naturally against the TOS of YNAB, I will not
document or endorse them here.
