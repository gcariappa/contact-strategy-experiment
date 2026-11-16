"""
Generates a SIMULATED dataset for a fictional SME lender and loads it into SQLite.
No real company data is used. Standard library only: no installs needed.

Run from the project folder:   python3 data/generate_data.py
Creates:  data/lender.db  plus one CSV per table in data/
"""
import csv, math, os, random, sqlite3
from datetime import date, timedelta

SEED = 2030                     # fixed seed: anyone re-running gets identical data
random.seed(SEED)
HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "lender.db")
N_CUSTOMERS = 20_000

SECTORS = ["Retail", "Hospitality", "Construction", "Professional services", "Manufacturing", "Health and beauty"]
SEGMENTS = [("Micro", 0.40), ("Small", 0.40), ("Medium", 0.20)]   # by annual turnover

# Behaviour of the abandoned-application reminder, by segment and test arm.
# The planted trade-off: day 1 lifts conversion everywhere, but in Micro it also
# raises unsubscribes and complaints and brings smaller, less reliably repaid loans.
REMINDER = {
    #          conv   unsub  complaint  loan_mult  repaid_on_time
    ("Micro",  "day3"): (0.190, 0.020, 0.004, 1.00, 0.88),
    ("Micro",  "day1"): (0.225, 0.055, 0.013, 0.85, 0.79),
    ("Small",  "day3"): (0.170, 0.020, 0.004, 1.00, 0.91),
    ("Small",  "day1"): (0.205, 0.025, 0.005, 1.00, 0.91),
    ("Medium", "day3"): (0.150, 0.018, 0.003, 1.00, 0.93),
    ("Medium", "day1"): (0.180, 0.022, 0.004, 1.00, 0.93),
}
LOAN_MEDIAN = {"Micro": 6_000, "Small": 15_000, "Medium": 35_000}   # GBP


def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def pick_segment():
    r, acc = random.random(), 0
    for name, share in SEGMENTS:
        acc += share
        if r < acc:
            return name
    return SEGMENTS[-1][0]


def loan_value(segment, mult):
    # Log-normal: most loans near the median, a long tail of large ones (realistic and noisy)
    return round(LOAN_MEDIAN[segment] * mult * math.exp(random.gauss(0, 0.6)), -2)


customers, applications, emails, outcomes = [], [], [], []
start = date(2026, 1, 5)
app_id = email_id = 0

for cid in range(1, N_CUSTOMERS + 1):
    signup = start + timedelta(days=random.randint(0, 180))
    segment = pick_segment()
    sector = random.choice(SECTORS)

    # Latent intent to borrow; the model score is a noisy estimate of it
    intent = random.gauss(0, 1)
    model_score = round(sigmoid(-2.6 + 1.2 * (intent + random.gauss(0, 0.6))), 4)
    customers.append([cid, signup.isoformat(), sector, segment, model_score])

    # ---- Journey 1: started an application? ---------------------------------
    p_start = sigmoid(-0.4 + 0.5 * intent)
    if random.random() < p_start:
        app_id += 1
        started = signup + timedelta(days=random.randint(0, 20))
        abandoned = random.random() < 0.68
        applications.append([app_id, cid, started.isoformat(),
                             "abandoned" if abandoned else "completed",
                             round(LOAN_MEDIAN[segment] * math.exp(random.gauss(0, 0.5)), -2)])
        if abandoned:
            # SPLIT TEST: randomly assign the reminder to day 1 or day 3 (50/50)
            arm = "day1" if random.random() < 0.5 else "day3"
            send_day = 1 if arm == "day1" else 3
            email_id += 1
            emails.append([email_id, cid, "abandoned_reminder", send_day, arm,
                           (started + timedelta(days=send_day)).isoformat()])
            conv, unsub, compl, mult, repay = REMINDER[(segment, arm)]
            conv *= 0.85 + 0.3 * sigmoid(intent)          # higher intent converts a bit more: noise, not signal
            converted = random.random() < conv
            outcomes.append([cid, "abandoned_reminder", int(converted),
                             loan_value(segment, mult) if converted else None,
                             int(random.random() < unsub), int(random.random() < compl),
                             (int(random.random() < repay) if converted else None)])
        continue

    # ---- Journey 2: never started -> model-driven re-engagement email -------
    # Rule: email the top 40% by model score, keep a random 10% hold-out from them,
    # and email a random 15% of everyone else as "exploration".
    p_base = sigmoid(-3.4 + 1.1 * intent)                  # chance of converting with no email
    uplift = 0.06 * math.exp(-((intent - 0.2) ** 2) / 0.7) - 0.006   # biggest in the middle, ~0 or negative at the ends
    # outcome filled in the second pass, once every customer has a score
    outcomes.append([cid, "reengagement", None, None, None, None, None, p_base, uplift, intent])

# ---- Second pass: apply the model's top-40% rule now that all scores exist ------
reeng = [o for o in outcomes if o[1] == "reengagement"]
score_of = {c[0]: c[4] for c in customers}
cutoff = sorted((score_of[o[0]] for o in reeng), reverse=True)[int(0.40 * len(reeng))]
for o in reeng:
    cid, p_base, uplift, intent = o[0], o[7], o[8], o[9]
    top = score_of[cid] >= cutoff
    emailed = (random.random() >= 0.10) if top else (random.random() < 0.15)
    if emailed:
        email_id += 1
        signup = date.fromisoformat(customers[cid - 1][1])
        emails.append([email_id, cid, "reengagement", 14, None, (signup + timedelta(days=14)).isoformat()])
    p = min(max(p_base + (uplift if emailed else 0), 0.001), 0.95)
    converted = random.random() < p
    unsub_p = 0.012 + 0.03 * (1 - sigmoid(intent)) if emailed else 0.0   # uninterested people unsubscribe more
    o[2:] = [int(converted),
             round(LOAN_MEDIAN[customers[cid - 1][3]] * math.exp(random.gauss(0, 0.6)), -2) if converted else None,
             int(random.random() < unsub_p),
             int(emailed and random.random() < 0.003),
             (int(random.random() < 0.9) if converted else None)]

# ---- Deliberately messy rows (about 1%), like real operational data -------------
for c in random.sample(customers, 300):                      # inconsistent sector labels
    c[2] = random.choice([c[2].lower(), c[2] + " ", c[2].upper()])
rem = [e for e in emails if e[2] == "abandoned_reminder"]
for e in random.sample(rem, 25):                              # duplicate sends logged twice
    email_id += 1
    emails.append([email_id] + e[1:])
for e in random.sample(rem, 15):                              # test arm not recorded
    e[4] = None
conv_rows = [o for o in outcomes if o[1] == "abandoned_reminder" and o[2] == 1]
for o in random.sample(conv_rows, 10):                        # converted but loan value missing
    o[3] = None
for a in random.sample(applications, 8):                      # application dated before sign-up
    c = customers[a[1] - 1]
    c[1] = (date.fromisoformat(a[2]) + timedelta(days=5)).isoformat()

# ---- Write SQLite + CSVs ---------------------------------------------------------
TABLES = {
    "customers": (["customer_id", "signup_date", "sector", "segment", "model_score"], customers),
    "applications": (["application_id", "customer_id", "started_date", "status", "amount_requested"], applications),
    "emails_sent": (["email_id", "customer_id", "email_type", "send_day", "test_arm", "sent_date"], emails),
    "outcomes": (["customer_id", "campaign", "converted", "loan_value", "unsubscribed", "complained", "repaid_on_time"],
                 [o[:7] for o in outcomes]),
}
if os.path.exists(DB):
    os.remove(DB)
con = sqlite3.connect(DB)
for name, (cols, rows) in TABLES.items():
    con.execute(f"CREATE TABLE {name} ({', '.join(cols)})")
    con.executemany(f"INSERT INTO {name} VALUES ({', '.join('?' * len(cols))})", rows)
    with open(os.path.join(HERE, f"{name}.csv"), "w", newline="") as f:
        w = csv.writer(f); w.writerow(cols); w.writerows(rows)
    print(f"{name:<13} {len(rows):>6,} rows")
con.commit(); con.close()
print(f"Saved {DB}")
