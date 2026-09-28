class Suggester:
    DEVICE_LIBRARY = {
        'electric_heating': {
            'name': 'Ogrzewanie elektryczne',
            'type': 'heating',
            'power_kw': 1.5,
            'usage_description': 'praca przez cały dzień',
            'daily_kwh': 18.0,
            'monthly_kwh_range': (120.0, 180.0, 250.0),
        },
        'air_conditioning': {
            'name': 'Klimatyzacja',
            'type': 'cooling',
            'power_kw': 1.4,
            'usage_description': 'praca w okresie chłodzenia',
            'daily_kwh': 14.0,
            'monthly_kwh_range': (70.0, 120.0, 180.0),
        },
        'refrigerator': {
            'name': 'Lodówka',
            'type': 'continuous',
            'power_kw': 0.9,
            'usage_description': 'ciągła praca',
            'daily_kwh': 0.9,
            'monthly_kwh_range': (20.0, 30.0, 45.0),
        },
        'automatic_pet_feeder': {
            'name': 'Automatyczna karmidło dla zwierząt',
            'type': 'scheduled',
            'power_kw': 0.01,
            'usage_description': 'krótkie cykle zasilania',
            'daily_kwh': 0.018,
            'monthly_kwh_range': (0.4, 0.6, 1.0),
        },
        'pet_camera': {
            'name': 'Kamera dla zwierząt',
            'type': 'continuous',
            'power_kw': 0.01,
            'usage_description': 'ciągła praca lub harmonogram',
            'daily_kwh': 0.18,
            'monthly_kwh_range': (2.0, 4.0, 7.0),
        },
        'router': {
            'name': 'Router Wi‑Fi',
            'type': 'continuous',
            'power_kw': 0.012,
            'usage_description': 'praca non-stop',
            'daily_kwh': 0.29,
            'monthly_kwh_range': (2.0, 4.0, 7.0),
        },
        'kettle': {
            'name': 'Czajnik',
            'type': 'burst',
            'power_kw': 2.0,
            'usage_description': 'krótkie użycia 3-5 min',
            'daily_kwh': 0.28,
            'monthly_kwh_range': (4.0, 8.0, 12.0),
        },
        'coffee_machine': {
            'name': 'Ekspres do kawy',
            'type': 'burst',
            'power_kw': 1.25,
            'usage_description': 'krótkie użycia 5-10 min',
            'daily_kwh': 0.22,
            'monthly_kwh_range': (3.0, 6.0, 10.0),
        },
        'oven': {
            'name': 'Piekarnik',
            'type': 'burst',
            'power_kw': 2.25,
            'usage_description': 'użycie w trakcie gotowania',
            'daily_kwh': 0.75,
            'monthly_kwh_range': (10.0, 18.0, 30.0),
        },
        'induction_hob': {
            'name': 'Płyta indukcyjna',
            'type': 'burst',
            'power_kw': 2.5,
            'usage_description': 'zużycie zależne od gotowania',
            'daily_kwh': 1.0,
            'monthly_kwh_range': (15.0, 25.0, 35.0),
        },
        'washing_machine': {
            'name': 'Pralka',
            'type': 'cycle',
            'power_kw': 0.8,
            'usage_description': 'jedna praca na cykl',
            'daily_kwh': 1.2,
            'monthly_kwh_range': (12.0, 18.0, 30.0),
        },
        'dishwasher': {
            'name': 'Zmywarka',
            'type': 'cycle',
            'power_kw': 1.0,
            'usage_description': 'jedna praca na cykl',
            'daily_kwh': 1.3,
            'monthly_kwh_range': (18.0, 24.0, 35.0),
        },
        'television': {
            'name': 'Telewizor',
            'type': 'active',
            'power_kw': 0.12,
            'usage_description': 'praca podczas oglądania',
            'daily_kwh': 0.8,
            'monthly_kwh_range': (8.0, 14.0, 24.0),
        },
        'gaming_console': {
            'name': 'Konsola do gier',
            'type': 'active',
            'power_kw': 0.15,
            'usage_description': 'gry i używanie przez długi czas',
            'daily_kwh': 1.0,
            'monthly_kwh_range': (10.0, 18.0, 25.0),
        },
        'laptop_computer': {
            'name': 'Laptop / komputer',
            'type': 'active',
            'power_kw': 0.15,
            'usage_description': 'używanie komputera',
            'daily_kwh': 1.1,
            'monthly_kwh_range': (10.0, 20.0, 30.0),
        },
        'lighting': {
            'name': 'Oświetlenie',
            'type': 'active',
            'power_kw': 0.1,
            'usage_description': 'oświetlenie aktywne',
            'daily_kwh': 1.2,
            'monthly_kwh_range': (10.0, 18.0, 30.0),
        },
        'phone_tablet_charging': {
            'name': 'Ładowanie telefonu / tabletu',
            'type': 'charging',
            'power_kw': 0.015,
            'usage_description': 'jedno ładowanie urządzenia',
            'daily_kwh': 0.12,
            'monthly_kwh_range': (1.0, 2.0, 4.0),
        },
        'standby_devices': {
            'name': 'Urządzenia w trybie standby',
            'type': 'standby',
            'power_kw': 0.04,
            'usage_description': 'gotowość do pracy',
            'daily_kwh': 0.96,
            'monthly_kwh_range': (10.0, 18.0, 30.0),
        },
    }

    def __init__(self):
        self.average_kilowatthours = 2.5
        self.minimal_kilowatthours = 1.6
        self.max_kilomatthours = 3.4

    def get_monthly_dataset(self):
        dataset = {}
        for device_key, config in self.DEVICE_LIBRARY.items():
            min_kwh, recommended_kwh, max_kwh = config['monthly_kwh_range']
            dataset[device_key] = {
                'name': config['name'],
                'type': config['type'],
                'power_kw': config['power_kw'],
                'usage_description': config['usage_description'],
                'daily_kwh': config['daily_kwh'],
                'monthly_kwh': round(config['daily_kwh'] * 30, 2),
                'min_monthly_kwh': min_kwh,
                'recommended_monthly_kwh': recommended_kwh,
                'max_monthly_kwh': max_kwh,
            }
        return dataset

    def get_device_advice(self, device_name, monthly_kwh):
        if device_name not in self.DEVICE_LIBRARY:
            raise KeyError(f'Unknown device: {device_name}')

        config = self.DEVICE_LIBRARY[device_name]
        min_kwh, recommended_kwh, max_kwh = config['monthly_kwh_range']

        if monthly_kwh > max_kwh:
            return {
                'device': device_name,
                'status': 'reduce',
                'message': (
                    f'Ogranicz korzystanie z {config["name"]}. Obecne zużycie {monthly_kwh} kWh/mies. jest wyższe '
                    f'niż zalecany limit {max_kwh} kWh/mies. Spróbuj zmniejszyć czas pracy o 20-40%.'
                ),
                'recommended_monthly_kwh': recommended_kwh,
            }

        if monthly_kwh < min_kwh:
            return {
                'device': device_name,
                'status': 'increase',
                'message': (
                    f'możesz sobie pozwolić na korzystanie z {config["name"]} trochę częściej. Obecne zużycie {monthly_kwh} kWh/mies. '
                    f'jest niżsowe od normy {min_kwh} kWh/mies., więc nie ma powodu do ograniczeń.'
                ),
                'recommended_monthly_kwh': recommended_kwh,
            }

        return {
            'device': device_name,
            'status': 'normal',
            'message': (
                f'Zużycie {config["name"]} jest w normie. Utrzymuj poziom około {recommended_kwh} kWh/mies., '
                f'aby nie przekroczyć bezpiecznego zakresu.'
            ),
            'recommended_monthly_kwh': recommended_kwh,
        }

    def get_usage_summary(self, device_usage):
        summary = []
        for device_name, monthly_kwh in device_usage.items():
            summary.append(self.get_device_advice(device_name, monthly_kwh))
        return summary

    @staticmethod
    def constants():
        return {'average_kilowatthours': 2.5, 'minimal_kilowatthours': 1.6, 'max_kilomatthours': 3.4}