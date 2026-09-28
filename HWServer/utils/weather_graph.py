import datetime
import requests


class WeatherGraph:
    ALLOWED_TYPES = ['daily', 'threedays', 'weekly']

    def __init__(self, lat=38.7167, lon=-9.1390):
        self.lat = lat
        self.lon = lon

    def _get_dynamic_labels(self, timestamp_key: str, times_iso: list) -> list:
        times = [datetime.datetime.fromisoformat(t) for t in times_iso]

        if timestamp_key == 'daily':
            return [t.strftime('%H:%M') for t in times[:24]]

        elif timestamp_key == 'threedays':
            return [t.strftime('%a %H:%M') for t in times[0:72:3]]

        elif timestamp_key == 'weekly':
            return [t.strftime('%a (%d.%m)') for t in times[:7]]

        else:
            raise KeyError(f'Unknown key: {timestamp_key}')

    def get_data(self, timestamp_key: str) -> dict:
        if timestamp_key not in self.ALLOWED_TYPES:
            raise KeyError(f'Unknown key: {timestamp_key}')

        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)

        if timestamp_key == 'daily':
            start_date = tomorrow.isoformat()
            end_date = start_date
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={self.lat}&longitude={self.lon}"
                f"&hourly=temperature_2m,relative_humidity_2m,cloud_cover,precipitation"
                f"&timezone=auto"
                f"&start_date={start_date}"
                f"&end_date={end_date}"
            )

        elif timestamp_key == 'threedays':
            start_date = tomorrow.isoformat()
            end_date = (today + datetime.timedelta(days=3)).isoformat()
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={self.lat}&longitude={self.lon}"
                f"&hourly=temperature_2m,relative_humidity_2m,cloud_cover,precipitation"
                f"&timezone=auto"
                f"&start_date={start_date}"
                f"&end_date={end_date}"
            )

        elif timestamp_key == 'weekly':
            start_date = tomorrow.isoformat()
            end_date = (today + datetime.timedelta(days=7)).isoformat()
            url = (
                f"https://api.open-meteo.com/v1/forecast?"
                f"latitude={self.lat}&longitude={self.lon}"
                f"&daily=temperature_2m_mean,relative_humidity_2m_mean,cloud_cover_mean,precipitation_sum"
                f"&timezone=auto"
                f"&start_date={start_date}"
                f"&end_date={end_date}"
            )

        response = requests.get(url, timeout=5)
        response.raise_for_status()

        if timestamp_key == 'weekly':
            daily = response.json().get('daily', {})
            labels = self._get_dynamic_labels(timestamp_key, daily.get('time', []))

            return {
                'timestamp_key': timestamp_key,
                'labels': labels,
                'temperature': daily.get('temperature_2m_mean', []),
                'humidity': daily.get('relative_humidity_2m_mean', []),
                'cloud_cover': daily.get('cloud_cover_mean', []),
                'precipitation': daily.get('precipitation_sum', []),
            }

        hourly = response.json().get('hourly', {})
        raw_times = hourly.get('time', [])

        labels = self._get_dynamic_labels(timestamp_key, raw_times)

        temp = hourly.get('temperature_2m', [])
        hum = hourly.get('relative_humidity_2m', [])
        cloud = hourly.get('cloud_cover', [])
        precip = hourly.get('precipitation', [])

        if timestamp_key == 'daily':
            t, h, c, p = temp[:24], hum[:24], cloud[:24], precip[:24]

        elif timestamp_key == 'threedays':
            t, h, c, p = (
                temp[0:72:3],
                hum[0:72:3],
                cloud[0:72:3],
                precip[0:72:3],
            )

        return {
            'timestamp_key': timestamp_key,
            'labels': labels,
            'temperature': t,
            'humidity': h,
            'cloud_cover': c,
            'precipitation': p,
        }