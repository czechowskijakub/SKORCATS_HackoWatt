class CheckboxGetter:
    def __init__(self):
        self.devices = {}

    @staticmethod
    def _to_bool(value):
        if isinstance(value, bool):
            return value
        if value is None:
            return False
        if isinstance(value, (int, float)):
            return bool(value)
        if isinstance(value, str):
            return value.strip().lower() in {'1', 'true', 'yes', 'on'}
        return bool(value)

    def collect_from_dict(self, data):
        if not isinstance(data, dict):
            raise TypeError('data must be a dict containing checkbox names and values')

        self.devices = {str(key): self._to_bool(value) for key, value in data.items()}
        return self.devices

    def collect_from_list(self, items, all_items=None):
        if not isinstance(items, list):
            raise TypeError('items must be a list of selected checkbox names')

        selected = {str(item) for item in items}
        if all_items is None:
            self.devices = {str(item): item in selected for item in selected}
            return self.devices

        self.devices = {str(item): str(item) in selected for item in all_items}
        return self.devices

    def from_request(self, request):
        if hasattr(request, 'POST'):
            self.devices = self.collect_from_dict(dict(request.POST))
            return self.devices

        if hasattr(request, 'data'):
            self.devices = self.collect_from_dict(request.data)
            return self.devices

        raise TypeError('request must provide POST or data payload')

    def normalize(self, data):
        if isinstance(data, dict):
            self.devices = self.collect_from_dict(data)
            return self.devices
        if isinstance(data, list):
            self.devices = self.collect_from_list(data)
            return self.devices
        raise TypeError('Unsupported checkbox payload type')

    def get_devices(self):
        return self.devices

    def set_devices(self, data):
        self.devices = self.collect_from_dict(data)
        return self.devices

    def clear_devices(self):
        self.devices = {}
        return self.devices
