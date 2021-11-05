# HOWTO: Downgrade from nYNAB to YNAB4

This page explains how to move from nYNAB to YNAB4 while retaining as much information as possible. See [Appendix
1](#appendix-1-ynab-4) for reasons and how to get YNAB4 running.

You will *export* your current nYNAB budget, then perform some scripted steps on the exported data, and then gradually
import it into a new YNAB4 budget. The scripted steps assume that you know how to use Python. (If anybody wants to
improve this guide with setup instructions, PRs are welcome!)

## Caveats

The process isn't automated and has some tricky steps – but if it goes wrong, you can always delete your YNAB4 data and
start again. Since we're starting with a new YNAB4 budget, nothing will be lost.

I also don't use many YNAB features including loans and separate credit card accounts, so the import might not work
correctly for them. Please open PRs with updates if you find required changes, or comment on the main issue if it worked
for you with a specific scenario, so others will know what works and what doesn't!

## Preliminaries

**In nYNAB:** Check if any of your category names contain a : or a `, as those are not valid characters in YNAB 4.
Change the category names now instead of having to go through

**In nYNAB:** Export your nYNAB budget by clicking on the budget name in the upper right hand corner → Export Budget.
Download the resulting zip file (once your browser has stopped freezing if your budget is a bit older), and export the
zip archive. It contains two files: `Budgetname as of date - Budget.csv` and `Budgetname as of date - Register.csv`.
I'll refer to these as `Budget.csv` and `Register.csv` from here on out.
   
**In YNAB4:** Install YNAB 4 (see [Appendix 1](#appendix-1-ynab-4)) and set up a new budget. Set the directory to some
place that works well for you (some location you will backup or sync, for example) in the File → Preferences dialog.
Then **close YNAB 4**. Go to the directory you selected: You will find a directory called `My Budget~number.ynab4`.
Inside, there is a `data1~number` directory, and inside that, there is a directory that is just one long UID, looking
like `98C499B4-4B29-6CC5-3B7A-F0247E9E2551`. Open this directory – it will contain a `budgetSettings.ybsettings` file
and a `Budget.yfull` file. I will call this directory "YNAB4 data directory" from here on out.

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
python create_categories.py path/to/ynab4_data_directory path/to/Budget.csv
```

## Step 3: Splitting the payment export file

```bash
python split_export.py path/to/nynab_data_directory/Register.csv
```

Will place one CSV file for each account in your working directory, and will replace some terms to make successful
imports more likely.

## Step 4: Importing files

You'll want to import every file next, each under the appropriate account. Make sure to select Year/Month/Date as time
format, as well as "Include transactions before account start date".

## Appendix 1: YNAB 4

YNAB 4 is a desktop application that was the predecessor of the web version, commonly called nYNAB (or just YNAB). YNAB
4 did not have a subscription model, but can't be purchased anymore. If you bought it back in the day, you can use your
activation key. You might also have bought it on Steam, where it will still be activated for you.

If you *didn't* purchase YNAB 4, you can still download it and run through the 1-month trial. There are trivial ways to
extend the trial duration, however, as those are naturally against the TOS of YNAB, I will not document or endorse them
here.
