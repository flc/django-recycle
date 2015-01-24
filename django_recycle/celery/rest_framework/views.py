from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from celery.result import AsyncResult
from celery.states import FAILURE


class TaskView(APIView):
    allowed_methods = ['get']

    permission_classes = (IsAuthenticated, )

    def get(self, request, format=None):
        task_id = request.QUERY_PARAMS.get("task_id", None)
        if not task_id:
            return Response({},
                            status=status.HTTP_400_BAD_REQUEST)

        result = AsyncResult(task_id)
        state, retval = result.state, result.result
        if state == FAILURE:
            # retval is an exception which is not serializable
            retval = ""
        response_data = dict(id=task_id, status=state, result=retval)
        return Response(response_data)
