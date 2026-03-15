from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsStaffForUnsafeMethods(BasePermission):
    """
    Разрешает небезопасные методы только сотрудникам с флагом is_staff.

    Безопасные методы доступны любому аутентифицированному пользователю.
    """

    def has_permission(self, request, view):
        """
        Проверяет доступ к endpoint в зависимости от HTTP-метода.

        :param request: HTTP-запрос.
        :param view: Представление DRF.
        :return: Признак наличия доступа.
        """
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)

        return bool(request.user and request.user.is_authenticated and request.user.is_staff)
