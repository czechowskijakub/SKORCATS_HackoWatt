import random

class TimestampsGraph:
    def __init__(self):
        self.timestamps = {
            'daily': [f'{hour:02d}:00' for hour in range(24)],
            'threedays': [
                f'{hour:02d}:00' 
                for day in range(1, 4) 
                for hour in range(0, 24, 3)
            ],
            'weekly': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        }

        self.intervals = {
            'daily': [0.0 for _ in range(24)],
            'threedays': [round(random.uniform(5.0, 15.0), 1) for _ in range(24)],
            'weekly': [0 for _ in range(7)],
        }

        self.populate_demo_data()

    def populate_demo_data(self):
        self.intervals['daily'] = [
            0.3, 0.2, 0.2, 0.1, 0.1, 0.2, 0.5, 1.1, 1.6, 1.8, 1.7, 1.9,
            1.6, 1.2, 1.0, 0.9, 1.1, 1.4, 1.7, 1.8, 1.5, 1.1, 0.8, 0.5,
        ]
        """self.intervals['threedays'] = [
            2.1, 1.8, 1.5, 3.4, 5.8, 7.2, 6.9, 5.1,  # Day 1 (8 wartości)
            4.2, 3.1, 2.8, 4.5, 8.4, 9.1, 7.7, 6.0,  # Day 2 (8 wartości)
            3.5, 2.9, 3.1, 5.0, 7.8, 8.2, 6.4, 4.1   # Day 3 (8 wartości)
        ]
        """
        self.intervals['weekly'] = [24, 30, 28, 26, 32, 36, 27]

    def get_labels(self, timestamp_key):
        if timestamp_key not in self.timestamps:
            raise KeyError(f'Unknown timestamp key: {timestamp_key}')
        return self.timestamps[timestamp_key]

    def update_data(self, timestamp_key: str, index: int, value):
        if timestamp_key not in self.intervals:
            raise KeyError(f'Unknown timestamp key: {timestamp_key}')

        values = self.intervals[timestamp_key]
        if index < 0 or index >= len(values):
            raise IndexError(f'Index {index} is out of range for {timestamp_key}')

        values[index] = float(value)
        self.intervals[timestamp_key] = values
        return values[index]

    def post_data(self, timestamp_key: str, values):
        if timestamp_key not in self.intervals:
            raise KeyError(f'Unknown timestamp key: {timestamp_key}')

        if not isinstance(values, list):
            raise TypeError('Values must be a list of numbers')

        expected_length = len(self.intervals[timestamp_key])
        if len(values) != expected_length:
            raise ValueError(
                f'Expected {expected_length} values for {timestamp_key}, got {len(values)}'
            )

        if timestamp_key == 'weekly':
            self.intervals[timestamp_key] = [int(value) for value in values]
        else:
            self.intervals[timestamp_key] = [float(value) for value in values]

        return {
            'timestamp_key': timestamp_key,
            'labels': self.timestamps[timestamp_key],
            'values': self.intervals[timestamp_key],
        }

    def get_data(self, timestamp_key):
        if timestamp_key not in self.intervals:
            raise KeyError(f'Unknown timestamp key: {timestamp_key}')
        return self.intervals[timestamp_key]