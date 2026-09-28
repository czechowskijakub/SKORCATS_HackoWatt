class Thresholds:

    def __init__(self):
        self.thresholds = {
            'standby': 0.15,
            'low': 0.8,
            'average': 2.0,
            'peak': 3.5,
        }

    def classify_thresholds(self, value_kW: float) -> str:
        if value_kW < self.thresholds['standby']:
            return 'standby'
        elif value_kW < self.thresholds['low']:
            return 'low'
        elif value_kW < self.thresholds['average']:
            return 'average'
        elif value_kW < self.thresholds['peak']:
            return 'peak'
        else:
            return 'critical'