import os
from decimal import Decimal
from datetime import datetime
import csv
import gspread
import time
import category_dict

files = []

for file in os.listdir(os.getcwd()):
    if file.endswith(".csv"):
        filename_parse = file.split("_")
        date_string = filename_parse[0]
        date = datetime.strptime(date_string, '%Y-%m-%d')
        files.append(file)

transactions = []
salary_stub_15 = (date.strftime('%Y-%m-15'), 'SDS Paystub', 'Salary', float('2115.60'))
salary_stub_30 = (date.strftime('%Y-%m-30'), 'SDS Paystub', 'Salary', float('2115.60'))
rent = (date.strftime('%Y-%m-15'), 'Rent', 'RENT & BILLS', float('-350'))

MONTH = date.strftime('%B').lower()

print(f'MONTH = {MONTH}')

def getTransactions(files):
    for file in files:
        with open(file, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader, None) #skipping header
            for row in csv_reader:
                if not row:
                    continue
                date = row[0]
                desc = row[3]
                if row[3] in category_dict.category_dict:
                    category = category_dict.category_dict.get(row[3])
                elif row[4] == 'Payment/Credit':
                    continue
                else:
                    category = row[4]
                if row[5] == '':
                    amt = float(row[6])
                else:
                    amt = float(f'-{row[5]}') # Credit means money in ex.Refunds
                transactions.append((date, desc, category, amt))
    return transactions

sa = gspread.service_account()
sh = sa.open("Personal Finances")

wks = sh.worksheet(f"{MONTH}")

target_row = 7 # Starts inputting data at row 7

wks.batch_clear([f'A{target_row}:D200'])

rows = getTransactions(files, None)

rows.append(salary_stub_15)
rows.append(salary_stub_30)
rows.appent(rent)


for row in rows:
    cell_range = f'A{target_row}:D{target_row}'
    wks.update(cell_range, [[row[0], row[1], row[2], row[3]]])
    target_row += 1
    time.sleep(1)
