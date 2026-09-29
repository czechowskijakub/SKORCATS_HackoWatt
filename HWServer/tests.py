from django.test import SimpleTestCase

from HWServer.utils.device_usage import DevicesConsumption
from HWServer.utils.suggester import Suggester


class SuggesterTests(SimpleTestCase):
    def test_dataset_contains_known_devices(self):
        dataset = Suggester().get_monthly_dataset()

        self.assertIn('electric_heating', dataset)
        self.assertIn('washing_machine', dataset)
        self.assertIn('router', dataset)

    def test_high_usage_triggers_reduction_advice(self):
        advice = Suggester().get_device_advice('electric_heating', monthly_kwh=500)

        self.assertEqual(advice['status'], 'reduce')
        self.assertIn('Ogranicz', advice['message'])

    def test_low_usage_allows_more_use(self):
        advice = Suggester().get_device_advice('router', monthly_kwh=1)

        self.assertEqual(advice['status'], 'increase')
        self.assertIn('możesz', advice['message'])


class DevicesConsumptionTests(SimpleTestCase):
    def test_toggle_updates_only_the_submitted_device(self):
        consumption = DevicesConsumption()
        consumption.populate_map()

        device_map = consumption.update_map(
            {'kettle': True},
            {'kettle': 12.5},
        )

        self.assertEqual(device_map['kettle'], 12.5)
        self.assertEqual(device_map['fridge'], 0)

        device_map = consumption.update_map(
            {'kettle': False},
            {'kettle': 12.5},
        )

        self.assertEqual(device_map['kettle'], 0)
