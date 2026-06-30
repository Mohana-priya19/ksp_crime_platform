import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

DISTRICTS = [
    "Bengaluru Urban", "Mysuru", "Mangaluru", "Hubballi-Dharwad",
    "Belagavi", "Kalaburagi", "Ballari", "Tumakuru", "Shivamogga",
    "Davangere", "Vijayapura", "Udupi", "Hassan", "Raichur", "Bagalkot"
]

DISTRICT_COORDS = {
    "Bengaluru Urban": (12.9716, 77.5946), "Mysuru": (12.2958, 76.6394),
    "Mangaluru": (12.9141, 74.8560), "Hubballi-Dharwad": (15.3647, 75.1240),
    "Belagavi": (15.8497, 74.4977), "Kalaburagi": (17.3297, 76.8200),
    "Ballari": (15.1394, 76.9214), "Tumakuru": (13.3379, 77.1173),
    "Shivamogga": (13.9299, 75.5681), "Davangere": (14.4644, 75.9218),
    "Vijayapura": (16.8302, 75.7100), "Udupi": (13.3409, 74.7421),
    "Hassan": (13.0033, 76.1004), "Raichur": (16.2120, 77.3566),
    "Bagalkot": (16.1691, 75.6615),
}

CRIME_TYPES = ["Theft", "Chain Snatching", "Robbery", "Burglary",
               "Vehicle Theft", "Assault", "Cheating/Fraud",
               "Kidnapping", "Dacoity", "Attempt to Murder", "Murder"]
CRIME_WEIGHTS = [0.25, 0.12, 0.10, 0.09, 0.10, 0.09, 0.08, 0.05, 0.04, 0.04, 0.04]

WEAPONS = ["None", "Knife", "Iron Rod", "Wooden Stick", "Firearm", "Stone"]
LOCATION_TYPES = ["Residential", "Commercial", "Road/Street", "Open Ground"]
CASE_STATUS = ["Open", "Closed", "Under Investigation", "Charge Sheeted"]

FIRST_NAMES = ["Raju", "Suresh", "Ramesh", "Mahesh", "Rajesh", "Venkatesh",
               "Prakash", "Ganesh", "Dinesh", "Santosh", "Lokesh", "Girish",
               "Lakshmi", "Savitha", "Meena", "Radha", "Kavitha", "Priya"]
LAST_NAMES = ["Kumar", "Gowda", "Reddy", "Naik", "Patil", "Rao", "Hegde",
              "Shetty", "Sharma", "Bhat", "Joshi", "Singh", "Yadav"]
STATIONS = ["Koramangala PS", "Jayanagar PS", "Shivajinagar PS",
            "Mysuru North PS", "Mangaluru Central PS", "Hubballi Town PS",
            "Belagavi Camp PS", "Kalaburagi PS", "Ballari Town PS"]

MASTER_CRIMINALS = [
    {
        "true_name": "Raju Kumar", "true_age": 28,
        "true_phone_last4": "4521", "true_district": "Bengaluru Urban",
        "crime_specialty": "Chain Snatching",
        "aliases": [
            {"name": "Rajesh K",   "age": 30, "district": "Mysuru"},
            {"name": "R. Kumar",   "age": 27, "district": "Mangaluru"},
            {"name": "Raju Gowda", "age": 29, "district": "Tumakuru"},
            {"name": "Raj Kumar",  "age": 31, "district": "Hubballi-Dharwad"},
            {"name": "Raju Naik",  "age": 28, "district": "Shivamogga"},
        ]
    },
    {
        "true_name": "Suresh Patil", "true_age": 35,
        "true_phone_last4": "7823", "true_district": "Belagavi",
        "crime_specialty": "Burglary",
        "aliases": [
            {"name": "Suresh P",    "age": 34, "district": "Vijayapura"},
            {"name": "S. Patil",    "age": 36, "district": "Bagalkot"},
            {"name": "Suresh Naik", "age": 35, "district": "Kalaburagi"},
        ]
    },
]

def random_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def random_phone():
    return f"9{random.randint(100000000, 999999999)}"

def random_date():
    start = datetime(2018, 1, 1)
    return start + timedelta(days=random.randint(0, 2000))

def random_coords(district):
    lat, lng = DISTRICT_COORDS.get(district, (13.0, 77.0))
    return round(lat + random.uniform(-0.3, 0.3), 6), \
           round(lng + random.uniform(-0.3, 0.3), 6)

def generate_fir_records(n=5000):
    records = []

    # Regular records
    for i in range(n):
        district = random.choice(DISTRICTS)
        lat, lng = random_coords(district)
        records.append({
            "fir_id":          f"FIR{str(i).zfill(6)}",
            "fir_date":        random_date().strftime("%Y-%m-%d"),
            "fir_time":        f"{random.randint(0,23):02d}:{random.randint(0,59):02d}",
            "district":        district,
            "police_station":  random.choice(STATIONS),
            "crime_type":      random.choices(CRIME_TYPES, weights=CRIME_WEIGHTS, k=1)[0],
            "location_type":   random.choice(LOCATION_TYPES),
            "latitude":        lat,
            "longitude":       lng,
            "accused_name":    random_name(),
            "accused_age":     random.randint(18, 60),
            "accused_address": f"{random.randint(1,999)}, Main Road, {district}",
            "accused_phone":   random_phone(),
            "accused_master_id": f"REAL_{str(i).zfill(5)}",
            "victim_name":     random_name(),
            "victim_age":      random.randint(15, 75),
            "victim_address":  f"{random.randint(1,999)}, Cross Road, {district}",
            "weapon_used":     random.choice(WEAPONS),
            "case_status":     random.choices(CASE_STATUS, weights=[0.35,0.30,0.25,0.10], k=1)[0],
        })

    # Master criminal aliases
    alias_count = 0
    for idx, criminal in enumerate(MASTER_CRIMINALS):
        all_ids = [{"name": criminal["true_name"], "age": criminal["true_age"],
                    "district": criminal["true_district"]}] + criminal["aliases"]
        for identity in all_ids:
            district = identity["district"]
            lat, lng = random_coords(district)
            phone = f"9{random.randint(1000000,9999999)}{criminal['true_phone_last4']}"
            records.append({
                "fir_id":          f"ALIAS{str(alias_count).zfill(4)}",
                "fir_date":        random_date().strftime("%Y-%m-%d"),
                "fir_time":        f"{random.randint(20,23):02d}:{random.randint(0,59):02d}",
                "district":        district,
                "police_station":  random.choice(STATIONS),
                "crime_type":      criminal["crime_specialty"],
                "location_type":   "Road/Street",
                "latitude":        lat,
                "longitude":       lng,
                "accused_name":    identity["name"],
                "accused_age":     identity["age"],
                "accused_address": f"{random.randint(1,999)}, Station Road, {district}",
                "accused_phone":   phone,
                "accused_master_id": f"MASTER_{idx:03d}",
                "victim_name":     random_name(),
                "victim_age":      random.randint(19, 70),
                "victim_address":  f"{random.randint(1,999)}, Park Road, {district}",
                "weapon_used":     "None",
                "case_status":     "Open",
            })
            alias_count += 1

    df = pd.DataFrame(records).sample(frac=1).reset_index(drop=True)
    print(f"Generated {len(df)} records ({alias_count} alias records for {len(MASTER_CRIMINALS)} master criminals)")
    return df

if __name__ == "__main__":
    import os
    os.makedirs("../data", exist_ok=True)
    df = generate_fir_records(5000)
    df.to_csv("../data/karnataka_fir_synthetic.csv", index=False)
    print("Saved to data/karnataka_fir_synthetic.csv")