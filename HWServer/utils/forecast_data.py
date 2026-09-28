import datetime
import math
from collections.abc import Mapping


DEVICE_COLUMNS = (
    'electric_heat_pump_kwh',
    'air_conditioning_kwh',
    'refrigerator_kwh',
    'pet_feeder_kwh',
    'pet_camera_kwh',
    'wifi_router_kwh',
    'kettle_kwh',
    'coffee_machine_kwh',
    'oven_kwh',
    'induction_hob_kwh',
    'washing_machine_kwh',
    'dishwasher_kwh',
    'television_kwh',
    'gaming_console_kwh',
    'laptop_computer_kwh',
    'lighting_kwh',
    'phone_charging_kwh',
    'standby_devices_kwh',
)

HABIT_COLUMNS = (
    'is_dog_in',
    'man_at_office',
    'girl_at_office',
    'weekend_away',
)

FEATURE_COLUMNS = (
    'temperature_2m',
    'apparent_temperature',
    'relative_humidity_2m',
    'direct_normal_irradiance',
    'shortwave_radiation',
    'cloud_cover',
    'wind_speed_10m',
    'cooling_demand',
    'heating_demand',
    'temp_rolling_mean_6h',
    'day_week',
    'is_weekend',
    'sin_hour',
    'cos_hour',
    'hour',
    'sin_year',
    'cos_year',
    *HABIT_COLUMNS,
    *DEVICE_COLUMNS,
)


class ForecastDataBuilder:
    COOLING_BASE_TEMP = 23.0
    HEATING_BASE_TEMP = 19.0

    @staticmethod
    def _number(value, field_name):
        if isinstance(value, bool):
            return int(value)
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f'{field_name} must be a finite number')
        return float(value)

    @staticmethod
    def _to_bool(value):
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return value.strip().lower() in {'1', 'true', 'yes', 'on'}
        return False

    def _device_values(self, devices):
        if not isinstance(devices, Mapping):
            raise ValueError('devices must be an object keyed by device feature name')

        values = {}
        for column in DEVICE_COLUMNS:
            device = devices.get(column, {})
            if not isinstance(device, Mapping):
                raise ValueError(f'devices.{column} must contain checked and kwh')

            checked = self._to_bool(device.get('checked', False))
            consumption = self._number(device.get('kwh', 0), f'devices.{column}.kwh')
            if consumption < 0:
                raise ValueError(f'devices.{column}.kwh cannot be negative')
            values[column] = consumption if checked else 0.0
        return values

    def _habit_values(self, habits, index, count):
        if not isinstance(habits, Mapping):
            raise ValueError('habits must be an object')

        values = {}
        for column in HABIT_COLUMNS:
            value = habits.get(column, 0)
            if isinstance(value, list):
                if len(value) != count:
                    raise ValueError(f'habits.{column} must have one value per forecast hour')
                value = value[index]
            values[column] = int(self._to_bool(value))
        return values

    def build(self, weather_records, forecast_date, devices, habits):
        if not isinstance(weather_records, list):
            raise ValueError('weather_records must be a list')

        if isinstance(forecast_date, str):
            forecast_date = datetime.date.fromisoformat(forecast_date)

        dated_records = []
        for record in weather_records:
            if not isinstance(record, Mapping) or 'time' not in record:
                raise ValueError('each weather record must contain a time')
            timestamp = datetime.datetime.fromisoformat(record['time'])
            dated_records.append((timestamp, record))
        dated_records.sort(key=lambda item: item[0])

        target_records = [
            (timestamp, record)
            for timestamp, record in dated_records
            if timestamp.date() == forecast_date
        ]
        if not target_records:
            raise ValueError(f'no weather records found for {forecast_date.isoformat()}')

        device_values = self._device_values(devices)
        timestamps = []
        rows = []

        for index, (timestamp, weather) in enumerate(target_records):
            weather_values = {
                key: self._number(weather.get(key), f'weather.{key}')
                for key in (
                    'temperature_2m',
                    'apparent_temperature',
                    'relative_humidity_2m',
                    'direct_normal_irradiance',
                    'shortwave_radiation',
                    'cloud_cover',
                    'wind_speed_10m',
                )
            }
            temperature = weather_values['temperature_2m']
            prior_temperatures = [
                self._number(record.get('temperature_2m'), 'weather.temperature_2m')
                for prior_time, record in dated_records
                if prior_time <= timestamp
            ]
            rolling_temperatures = prior_temperatures[-6:]

            day_of_year = timestamp.timetuple().tm_yday
            hour_angle = 2 * math.pi * timestamp.hour / 24
            year_angle = 2 * math.pi * day_of_year / 366
            date_values = {
                'cooling_demand': max(temperature - self.COOLING_BASE_TEMP, 0.0),
                'heating_demand': max(self.HEATING_BASE_TEMP - temperature, 0.0),
                'temp_rolling_mean_6h': sum(rolling_temperatures) / len(rolling_temperatures),
                'day_week': timestamp.weekday() + 1,
                'is_weekend': int(timestamp.weekday() >= 5),
                'sin_hour': math.sin(hour_angle),
                'cos_hour': math.cos(hour_angle),
                'hour': timestamp.hour,
                'sin_year': math.sin(year_angle),
                'cos_year': math.cos(year_angle),
            }
            row_values = {
                **weather_values,
                **date_values,
                **self._habit_values(habits, index, len(target_records)),
                **device_values,
            }
            rows.append([row_values[column] for column in FEATURE_COLUMNS])
            timestamps.append(timestamp.isoformat())

        return timestamps, rows