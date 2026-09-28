import json
import requests

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from HWServer.utils.checkbox_getter import CheckboxGetter
from HWServer.utils.timestamps_graph import TimestampsGraph
from HWServer.utils.weather_graph import WeatherGraph
from HWServer.utils.thresholds import Thresholds


@csrf_exempt
def receive_json(request):
    if request.method == "OPTIONS":
        response = JsonResponse({"status": "ok"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
        return response

    if request.method != "POST":
        return JsonResponse({"status": "only_post_allowed"}, status=405)

    request_body = request.body.decode("utf-8")
    if not request_body.strip():
        return JsonResponse({"status": "empty_body"}, status=400)

    try:
        payload = json.loads(request_body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "invalid_json"}, status=400)

    print("Received JSON payload:", payload)

    normalized_devices = CheckboxGetter().collect_from_dict(payload)
    print("Normalized devices:", normalized_devices)

    response = JsonResponse({
        "status": "ok",
        "devices": normalized_devices
    })
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
    response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    return response


@csrf_exempt
def graph_data(request):
    graph = TimestampsGraph()
    series_type = request.GET.get("type", "daily")

    if series_type == "all":
        payload = {}
        for key in graph.timestamps:
            payload[key] = {
                "labels": graph.get_labels(key),
                "values": graph.get_data(key),
            }
    elif series_type in graph.timestamps:
        payload = {
            "timestamp_key": series_type,
            "labels": graph.get_labels(series_type),
            "values": graph.get_data(series_type),
        }
    else:
        return JsonResponse({"status": "invalid_type", "allowed": list(graph.timestamps.keys())}, status=400)

    response = JsonResponse(payload)
    response["Access-Control-Allow-Origin"] = "*"
    response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, X-CSRFToken"
    return response

@csrf_exempt
def weather_data(request):
    series_type = request.GET.get('type', 'daily')

    try:
        weather = WeatherGraph()

        if series_type == 'all':
            payload = {
                key: weather.get_data(key) for key in weather.ALLOWED_TYPES
            }
        elif series_type in weather.ALLOWED_TYPES:
            payload = weather.get_data(series_type)
        else:
            return JsonResponse(
                {
                    'status': 'invalid_type',
                    'allowed': weather.ALLOWED_TYPES,
                },
                status=400,
            )

        response = JsonResponse(payload)
        response['Access-Control-Allow-Origin'] = '*'
        return response

    except requests.exceptions.RequestException as e:
        return JsonResponse(
            {'error': f'Weather API error: {str(e)}'}, status=500
        )
    except Exception as e:
        return JsonResponse({'error': f'Internal err: {str(e)}'}, status=500)

def hello_world(request):
    return HttpResponse("Hello, world!")

