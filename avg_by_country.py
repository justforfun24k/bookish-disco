import csv
from collections import defaultdict

# ---------- read CSV ----------
data=defaultdict(list)  #{country:[scores]}

with open('remote_work_survey.csv',newline='') as f:
    reader=csv.DictReader(f)
    for row in reader:
        score=int(row['productivity_score'])
        if 0<= score <=100:
            data[row['country']].append(score)
# ---------- compute averages ----------
averages={c: round(sum(vals) / len(vals),1) for c,vals in data.items()}
# ---------- pretty print ----------
print('| Country | Avg_Score |')
print('|---------|-----------|')
for c in sorted(averages):
    print(f'| {c:<7} | {averages[c]:>9.1f} |')