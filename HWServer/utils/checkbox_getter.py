class CheckboxGetter:
    
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

        return {str(key): self._to_bool(value) for key, value in data.items()}

    def collect_from_list(self, items, all_items=None):
        if not isinstance(items, list):
            raise TypeError('items must be a list of selected checkbox names')

        selected = {str(item) for item in items}
        if all_items is None:
            return {str(item): item in selected for item in selected}

        return {str(item): str(item) in selected for item in all_items}

    def from_request(self, request):
        if hasattr(request, 'POST'):
            return self.collect_from_dict(dict(request.POST))

        if hasattr(request, 'data'):
            return self.collect_from_dict(request.data)

        raise TypeError('request must provide POST or data payload')

    def normalize(self, data):
        if isinstance(data, dict):
            return self.collect_from_dict(data)
        if isinstance(data, list):
            return self.collect_from_list(data)
        raise TypeError('Unsupported checkbox payload type')
