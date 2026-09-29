import numpy as np
import pandas as pd
from pathlib import Path

class DevicesConsumption():
    DEVICE_COLUMNS = {
        "fridge": "refrigerator_kwh",
        "wifi": "wifi_router_kwh",
        "camera": "pet_camera_kwh",
        "dog_feeder": "pet_feeder_kwh",
        "lighting": "lighting_kwh",
        "computer": "laptop_computer_kwh",
        "console": "gaming_console_kwh",
        "heating": "electric_heat_pump_kwh",
        "coffee_machine": "coffee_machine_kwh",
        "AC": "air_conditioning_kwh",
        "dishwasher": "dishwasher_kwh",
        "kettle": "kettle_kwh",
        "oven": "oven_kwh",
        "conduction_stove": "induction_hob_kwh",
        "tv": "television_kwh",
        "washing_machine": "washing_machine_kwh",
    }

    def __init__(self):
        self.devices_map = {}
        
    def populate_map(self):
        self.devices_map = {
            "fridge": 0,
            "wifi": 0,
            "camera": 0,
            "dog_feeder": 0,
            "lighting": 0,
            "EV": 0,
            "computer": 0,
            "console": 0,
            "heating": 0,
            "coffee_machine": 0,
            "AC": 0,
            "dishwasher": 0,
            "kettle": 0,
            "oven": 0,
            "conduction_stove": 0,
            "tv": 0,
            "washing_machine": 0
        }
        return self.devices_map

    def update_map(self, devices, consumption_by_device):
        for device, is_on in devices.items():
            if device not in self.devices_map:
                continue
            self.devices_map[device] = (
                consumption_by_device.get(device, 0) if is_on else 0
            )
        return self.devices_map.copy()

    def evaluate(self, save_profile=True):
        # 1. Wczytanie pliku z danymi pogodowymi i obecnością
        data_path = Path(__file__).resolve().parents[2] / "weather_features_with_behavior.csv"
        df = pd.read_csv(data_path)
        np.random.seed(42)
        n = len(df)

        # Określenie fizycznej obecności domowników w mieszkaniu
        man_at_home = np.where(df["weekend_away"] == 1, 0, 1 - df["man_at_office"])
        girl_at_home = np.where(df["weekend_away"] == 1, 0, 1 - df["girl_at_office"])
        people_at_home = man_at_home + girl_at_home
        is_anyone_home = (people_at_home > 0).astype(int)

        # Podział doby na 4 przedziały czasowe z Twojej tabeli
        hour = df["hour"]
        morn = (hour >= 6) & (hour < 9)    # 6-9
        work = (hour >= 9) & (hour < 17)   # 9-17
        eve = (hour >= 17) & (hour < 23)   # 17-23
        night = (hour >= 23) | (hour < 6)  # 23-6 NOC

        # =====================================================================
        # SYMULACJA 18 URZĄDZEŃ (Zużycie w kWh w danej godzinie)
        # =====================================================================

        # 1. Pompa ciepła / Ogrzewanie elektryczne (1.0 - 2.5 kW)
        # 9-17 (O): zależne od chłodu i psa/ludzi; 17-23 (X): wieczorne dogrzewanie
        heat_cond_work = work & (df["heating_demand"] > 0) & ((is_anyone_home == 1) | (df["is_dog_in"] == 1))
        heat_cond_eve = eve & (df["heating_demand"] > 0) & ((is_anyone_home == 1) | (df["is_dog_in"] == 1))
        app_heat = np.zeros(n)
        app_heat[heat_cond_work] = np.clip(0.6 + df.loc[heat_cond_work, "heating_demand"] * 0.20, 0.8, 2.2)
        app_heat[heat_cond_eve] = np.clip(0.8 + df.loc[heat_cond_eve, "heating_demand"] * 0.25, 1.0, 2.5)

        # 2. Klimatyzacja (0.8 - 2.0 kW)
        # 9-17 (O): upał w dzień w Lizbonie dla psa/ludzi; 17-23 (X): schładzanie wieczorne
        ac_cond_work = work & (df["cooling_demand"] > 0) & ((is_anyone_home == 1) | (df["is_dog_in"] == 1))
        ac_cond_eve = eve & (df["cooling_demand"] > 0) & ((is_anyone_home == 1) | (df["is_dog_in"] == 1))
        app_ac = np.zeros(n)
        app_ac[ac_cond_work] = np.clip(0.6 + df.loc[ac_cond_work, "cooling_demand"] * 0.20, 0.8, 2.0)
        app_ac[ac_cond_eve] = np.clip(0.7 + df.loc[ac_cond_eve, "cooling_demand"] * 0.22, 0.8, 2.0)

        # 3. Lodówka (0.8 - 1.2 kWh/dzień -> X 24/7)
        app_fridge = 0.035 + 0.0004 * df["temperature_2m"].clip(lower=10, upper=40)

        # 4. Automatyczny karmnik (0.005 - 0.02 kWh/dzień -> O: tylko gdy pies w domu)
        app_feeder = np.where(df["is_dog_in"] == 1, 0.012 / 24.0, 0.0)

        # 5. Kamera dla psa (0.005 - 0.015 kW -> O: tylko gdy pies w domu)
        app_camera = np.where(df["is_dog_in"] == 1, 0.009, 0.0)

        # 6. Wi-Fi router (0.008 - 0.015 kW -> X 24/7)
        app_wifi = np.full(n, 0.010)

        # 7. Czajnik (2.0 kW, 3-5 min -> ~0.13 kWh/użycie)
        # 6-9 (X), 9-17 (O - praca zdalna)
        app_kettle = np.zeros(n)
        app_kettle[morn] = people_at_home[morn] * 0.08
        kettle_wfh_prob = np.random.rand(n) < 0.20
        app_kettle[work & (people_at_home > 0) & kettle_wfh_prob] = 0.13

        # 8. Ekspres do kawy (1.0 - 1.5 kW -> ~0.14 kWh/użycie)
        # 6-9 (X), 9-17 (O - praca zdalna popołudniu)
        app_coffee = np.zeros(n)
        app_coffee[morn] = people_at_home[morn] * 0.10
        coffee_wfh_prob = (np.random.rand(n) < 0.25) & df["hour"].isin([13, 14, 15])
        app_coffee[work & (people_at_home > 0) & coffee_wfh_prob] = 0.14

        # 9. Piekarnik (2.0 - 2.5 kW -> 17-23: X, ~2-3 razy w tyg.)
        app_oven = np.zeros(n)
        oven_prob = (np.random.rand(n) < 0.20) & df["hour"].isin([18, 19, 20]) & (is_anyone_home == 1)
        app_oven[eve & oven_prob] = np.random.uniform(1.1, 1.6, n)[eve & oven_prob]

        # 10. Płyta indukcyjna (1.5 - 3.5 kW -> 17-23: X, codzienne gotowanie)
        app_induction = np.zeros(n)
        induction_prob = (np.random.rand(n) < 0.55) & df["hour"].isin([18, 19, 20]) & (is_anyone_home == 1)
        app_induction[eve & induction_prob] = np.random.uniform(0.7, 1.3, n)[eve & induction_prob]

        # 11. Pralka (0.6 - 1.0 kWh/cykl -> 17-23: X, elastyczne AGD)
        app_washing = np.zeros(n)
        wash_prob = (np.random.rand(n) < 0.22) & df["hour"].isin([18, 19, 20, 21]) & (is_anyone_home == 1)
        app_washing[eve & wash_prob] = np.random.uniform(0.7, 0.95, n)[eve & wash_prob]

        # 12. Zmywarka (0.8 - 1.2 kWh/cykl -> 17-23: X, elastyczne AGD)
        app_dishwasher = np.zeros(n)
        dish_prob = (np.random.rand(n) < 0.45) & df["hour"].isin([20, 21, 22]) & (is_anyone_home == 1)
        app_dishwasher[eve & dish_prob] = np.random.uniform(0.85, 1.15, n)[eve & dish_prob]

        # 13. Telewizor (0.08 - 0.15 kW -> 17-23: X)
        app_tv = np.zeros(n)
        tv_prob = (np.random.rand(n) < 0.70) & (is_anyone_home == 1)
        app_tv[eve & tv_prob] = np.random.uniform(0.09, 0.13, n)[eve & tv_prob]

        # 14. Konsola do gier (0.10 - 0.20 kW -> 17-23: X)
        app_gaming = np.zeros(n)
        gaming_prob = (np.random.rand(n) < 0.35) & df["hour"].isin([19, 20, 21, 22]) & (is_anyone_home == 1)
        app_gaming[eve & gaming_prob] = np.random.uniform(0.12, 0.18, n)[eve & gaming_prob]

        # 15. Laptop / komputer (0.05 - 0.25 kW -> 6-9: X, 9-17: O (WFH), 17-23: X)
        app_laptop = np.zeros(n)
        app_laptop[morn] = people_at_home[morn] * 0.05
        app_laptop[work] = people_at_home[work] * 0.12
        app_laptop[eve & (is_anyone_home == 1)] = 0.08

        # 16. Oświetlenie (0.05 - 0.15 kW -> 6-9: X, 17-23: X)
        app_lighting = np.zeros(n)
        app_lighting[morn & (is_anyone_home == 1)] = 0.08
        app_lighting[eve & (is_anyone_home == 1)] = 0.10

        # 17. Ładowanie telefonów (0.005 - 0.02 kWh -> 6-9: X, 9-17: O, 17-23: X)
        app_charging = np.zeros(n)
        app_charging[morn] = people_at_home[morn] * 0.008
        app_charging[work] = people_at_home[work] * 0.006
        app_charging[eve] = people_at_home[eve] * 0.015

        # 18. Standby devices (0.02 - 0.06 kW -> X 24/7)
        app_standby = np.full(n, 0.035)

        # =====================================================================
        # PRZYPISANIE DO KOLUMN ORAZ SUMOWANIE DO DOCELOWEGO Y (total_kwh)
        # =====================================================================
        appliance_cols = [
            "electric_heat_pump_kwh", "air_conditioning_kwh", "refrigerator_kwh",
            "pet_feeder_kwh", "pet_camera_kwh", "wifi_router_kwh", "kettle_kwh",
            "coffee_machine_kwh", "oven_kwh", "induction_hob_kwh", "washing_machine_kwh",
            "dishwasher_kwh", "television_kwh", "gaming_console_kwh", "laptop_computer_kwh",
            "lighting_kwh", "phone_charging_kwh", "standby_devices_kwh"
        ]

        app_data = [
            app_heat, app_ac, app_fridge, app_feeder, app_camera, app_wifi, app_kettle,
            app_coffee, app_oven, app_induction, app_washing, app_dishwasher, app_tv,
            app_gaming, app_laptop, app_lighting, app_charging, app_standby
        ]

        for col, data in zip(appliance_cols, app_data):
            df[col] = np.round(data, 4)

        # NASZ TARGET GŁÓWNY:
        df["total_kwh"] = np.round(df[appliance_cols].sum(axis=1), 4)

        if save_profile:
            df.to_csv("household_full_profile.csv", index=False)
            print("Profil godzinowy zapisany pomyślnie do pliku 'household_full_profile.csv'!")

        consumption_by_device = {}
        for device, column in self.DEVICE_COLUMNS.items():
            active_usage = df.loc[df[column] > 0, column]
            consumption_by_device[device] = (
                round(float(active_usage.mean()), 4)
                if not active_usage.empty
                else 0
            )
        return consumption_by_device