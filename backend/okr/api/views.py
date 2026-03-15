from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common_utils.api import IsStaffForUnsafeMethods
from okr.api.serializers import (
    CheckInCreateSerializer,
    CheckInUpdateSerializer,
    CommentCreateSerializer,
    KeyResultCreateSerializer,
    KeyResultUpdateSerializer,
    OkrCreateSerializer,
    OkrDetailSerializer,
    OkrListSerializer,
    OkrUpdateSerializer,
    QuarterCreateSerializer,
    QuarterSerializer,
)
from okr.selectors import (
    get_check_ins,
    get_key_results,
    get_okr_by_id,
    get_okr_detail_queryset,
    get_okrs,
    get_quarters,
    hydrate_okr_detail,
)
from okr.services.checkins import delete_check_in


class QuarterListAPIView(APIView):
    permission_classes = [IsStaffForUnsafeMethods]

    def get(self, request):
        """
        Возвращает список доступных кварталов.

        :param request: HTTP-запрос аутентифицированного пользователя.
        :return: HTTP-ответ со списком кварталов.
        """
        serializer = QuarterSerializer(get_quarters(), many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Создаёт новый квартал.

        :param request: HTTP-запрос с данными квартала.
        :return: HTTP-ответ с созданным кварталом.
        """
        serializer = QuarterCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quarter = serializer.save()
        return Response(QuarterSerializer(quarter).data, status=201)


class QuarterDetailAPIView(APIView):
    permission_classes = [IsStaffForUnsafeMethods]

    def patch(self, request, quarter_id: int):
        """
        Обновляет существующий квартал.

        :param request: HTTP-запрос с новыми данными квартала.
        :param quarter_id: Идентификатор квартала.
        :return: HTTP-ответ с обновлённым кварталом.
        :raises Http404: Если квартал с указанным идентификатором не найден.
        """
        quarter = get_object_or_404(get_quarters(), id=quarter_id)
        serializer = QuarterCreateSerializer(instance=quarter, data=request.data)
        serializer.is_valid(raise_exception=True)
        updated_quarter = serializer.save()
        return Response(QuarterSerializer(updated_quarter).data)


class OkrListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Возвращает список OKR с фильтрами для рабочего экрана.

        :param request: HTTP-запрос с query-параметрами quarter, status и team_id.
        :return: HTTP-ответ со списком OKR.
        """
        okrs = get_okrs(
            quarter_name=request.query_params.get('quarter') or None,
            status=request.query_params.get('status') or None,
            team_id=int(request.query_params['team_id']) if request.query_params.get('team_id') else None,
        )
        serializer = OkrListSerializer(okrs, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Создаёт новую цель OKR.

        :param request: HTTP-запрос с данными OKR и ключевых результатов.
        :return: HTTP-ответ с созданной целью OKR.
        """
        serializer = OkrCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        okr = serializer.save()
        return Response(OkrDetailSerializer(get_okr_by_id(okr.id)).data, status=201)


class OkrDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, okr_id: int):
        """
        Возвращает детальную карточку OKR.

        :param request: HTTP-запрос аутентифицированного пользователя.
        :param okr_id: Идентификатор цели OKR.
        :return: HTTP-ответ с детальными данными OKR.
        :raises Http404: Если OKR с указанным идентификатором не найден.
        """
        okr = hydrate_okr_detail(get_object_or_404(get_okr_detail_queryset(), id=okr_id))
        serializer = OkrDetailSerializer(okr)
        return Response(serializer.data)

    def patch(self, request, okr_id: int):
        """
        Обновляет существующую цель OKR.

        :param request: HTTP-запрос с новыми данными OKR.
        :param okr_id: Идентификатор цели OKR.
        :return: HTTP-ответ с обновлёнными данными OKR.
        :raises Http404: Если OKR с указанным идентификатором не найден.
        """
        okr = hydrate_okr_detail(get_object_or_404(get_okr_detail_queryset(), id=okr_id))
        serializer = OkrUpdateSerializer(instance=okr, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        updated_okr = serializer.save()
        return Response(OkrDetailSerializer(get_okr_by_id(updated_okr.id)).data)


class OkrKeyResultListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, okr_id: int):
        """
        Создаёт новый ключевой результат для существующего OKR.

        :param request: HTTP-запрос с данными ключевого результата.
        :param okr_id: Идентификатор цели OKR.
        :return: HTTP-ответ с обновлённой карточкой OKR.
        :raises Http404: Если OKR с указанным идентификатором не найден.
        """
        okr = hydrate_okr_detail(get_object_or_404(get_okr_detail_queryset(), id=okr_id))
        serializer = KeyResultCreateSerializer(
            data=request.data,
            context={'request': request, 'okr': okr},
        )
        serializer.is_valid(raise_exception=True)
        key_result = serializer.save()
        return Response(OkrDetailSerializer(get_okr_by_id(key_result.okr_id)).data, status=201)


class OkrCommentListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, okr_id: int):
        """
        Создаёт комментарий для существующего OKR.

        :param request: HTTP-запрос с текстом комментария.
        :param okr_id: Идентификатор цели OKR.
        :return: HTTP-ответ с обновлённой карточкой OKR.
        :raises Http404: Если OKR с указанным идентификатором не найден.
        """
        okr = hydrate_okr_detail(get_object_or_404(get_okr_detail_queryset(), id=okr_id))
        serializer = CommentCreateSerializer(
            data=request.data,
            context={'request': request, 'okr': okr},
        )
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        return Response(OkrDetailSerializer(get_okr_by_id(comment.okr_id)).data, status=201)


class KeyResultDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, key_result_id: int):
        """
        Обновляет существующий ключевой результат.

        :param request: HTTP-запрос с новыми данными ключевого результата.
        :param key_result_id: Идентификатор ключевого результата.
        :return: HTTP-ответ с обновлённой карточкой OKR.
        :raises Http404: Если ключевой результат с указанным идентификатором не найден.
        """
        key_result = get_object_or_404(get_key_results(), id=key_result_id)
        serializer = KeyResultUpdateSerializer(instance=key_result, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        updated_key_result = serializer.save()
        return Response(OkrDetailSerializer(get_okr_by_id(updated_key_result.okr_id)).data)


class KeyResultCheckInListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, key_result_id: int):
        """
        Создаёт check-in для существующего ключевого результата.

        :param request: HTTP-запрос с данными check-in.
        :param key_result_id: Идентификатор ключевого результата.
        :return: HTTP-ответ с обновлённой карточкой OKR.
        :raises Http404: Если ключевой результат с указанным идентификатором не найден.
        """
        key_result = get_object_or_404(get_key_results(), id=key_result_id)
        serializer = CheckInCreateSerializer(
            data=request.data,
            context={'request': request, 'key_result': key_result},
        )
        serializer.is_valid(raise_exception=True)
        check_in = serializer.save()
        return Response(OkrDetailSerializer(get_okr_by_id(check_in.key_result.okr_id)).data, status=201)


class CheckInDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, check_in_id: int):
        """
        Обновляет существующий check-in.

        :param request: HTTP-запрос с новыми данными check-in.
        :param check_in_id: Идентификатор check-in.
        :return: HTTP-ответ с обновлённой карточкой OKR.
        :raises Http404: Если check-in с указанным идентификатором не найден.
        """
        check_in = get_object_or_404(get_check_ins(), id=check_in_id)
        serializer = CheckInUpdateSerializer(instance=check_in, data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        updated_check_in = serializer.save()
        return Response(OkrDetailSerializer(get_okr_by_id(updated_check_in.key_result.okr_id)).data)

    def delete(self, request, check_in_id: int):
        """
        Удаляет существующий check-in.

        :param request: HTTP-запрос аутентифицированного пользователя.
        :param check_in_id: Идентификатор check-in.
        :return: HTTP-ответ с обновлённой карточкой OKR.
        :raises Http404: Если check-in с указанным идентификатором не найден.
        """
        check_in = get_object_or_404(get_check_ins(), id=check_in_id)
        okr_id = delete_check_in(check_in=check_in, deleted_by=request.user)
        return Response(OkrDetailSerializer(get_okr_by_id(okr_id)).data)
