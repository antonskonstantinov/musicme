from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status


def _stringify_details(detail):
    if isinstance(detail, dict):
        return {key: _stringify_details(value) for key, value in detail.items()}
    if isinstance(detail, list):
        return [str(item) for item in detail]
    return str(detail)


def api_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is None:
        return Response(
            {
                "error": {
                    "code": "internal_error",
                    "message": "Внутренняя ошибка сервера",
                    "details": {},
                }
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    status_code = response.status_code
    data = response.data
    details = {}
    code = "validation_error"
    message = "Некорректные данные"

    if status_code == status.HTTP_404_NOT_FOUND:
        code = "not_found"
        message = "Ресурс не найден"
        if isinstance(data, dict) and "detail" in data:
            message = str(data["detail"])
        elif isinstance(data, list) and data:
            message = str(data[0])
    elif status_code == status.HTTP_400_BAD_REQUEST:
        code = "validation_error"
        if isinstance(data, dict):
            if list(data.keys()) == ["detail"]:
                message = str(data["detail"])
            else:
                details = _stringify_details(data)
        elif isinstance(data, list) and data:
            message = str(data[0])
    elif status_code == status.HTTP_401_UNAUTHORIZED:
        code = "authentication_required"
        message = "Требуется аутентификация"
    elif status_code == status.HTTP_403_FORBIDDEN:
        code = "permission_denied"
        message = "Недостаточно прав"
    elif status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        code = "method_not_allowed"
        message = "Метод не поддерживается"

    response.data = {
        "error": {
            "code": code,
            "message": message,
            "details": details,
        }
    }
    return response
