from django.http import JsonResponse


def api_root(request):
    return JsonResponse(
        {
            "data": {
                "name": "Muzzzic API",
                "version": "v1",
                "status": "ok",
            }
        }
    )
