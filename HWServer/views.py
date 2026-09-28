import json

from django.http import HttpResponse

from HWServer.utils.suggester import Suggester

from django.http import JsonResponse

from HWServer.utils.checkbox_getter import CheckboxGetter

def receive_json(request):
    if request.method != "POST":
        return JsonResponse({"status": "only_post_allowed"}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"status": "invalid_json"}, status=400)

    cleaned = CheckboxGetter().collect_from_dict(payload)

    return JsonResponse({
        "status": "ok",
        "devices": cleaned
    })
    
def hello_world(request):
    return HttpResponse("Hello, world!")


def suggest_devices(request):
    suggester = Suggester()
    dataset = suggester.get_monthly_dataset()

    example_usage = {
        'electric_heating': 500,
        'air_conditioning': 90,
        'router': 1,
        'washing_machine': 20,
    }

    suggestions = [
        {
            'device': device,
            'advice': suggester.get_device_advice(device, usage),
            'monthly_kwh': dataset[device]['monthly_kwh'],
        }
        for device, usage in example_usage.items()
    ]

    return HttpResponse(
        json.dumps({'dataset': dataset, 'suggestions': suggestions}, ensure_ascii=False),
        content_type='application/json; charset=utf-8',
    )

