from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from assessments.models import StudentAssessmentAttempt
from .utils.encryption_handler import Data_Encryption
import json
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode, urlencode

from .utils.request_to_server import _request
import datetime


models_mapping = {
    "StudentAssessmentAttempt": StudentAssessmentAttempt
}

data_encryption = Data_Encryption()


def __tab_behavior_logger(request, id, target, data):
    attempt = models_mapping[target].objects.get(pk=id)

    attempt.is_proctored = True

    tab_behavior = attempt.proctoring_data.get("tab_behavior", {})
    tab_behavior[len(tab_behavior)] = data

    attempt.proctoring_data["tab_behavior"] = tab_behavior

    attempt.save()


def __face_behavior_detector(request, id, target, data):
    response = _request(api_name="face_detector", json=data)
    
    attempt = models_mapping[target].objects.get(pk=id)
    attempt.is_proctored = True

    response_data = response.get('data', {})
    # last_face_behavior_state = request.session.get('face_behavior', None)

    # request.session['face_behavior'] = response_data
    # cache.set(f"face_behavior_{request.user.id}_{attempt_pk}", data, timeout=10)
    # print(last_face_behavior_state)
    # print(response_data)

    face_behavior_dict = attempt.proctoring_data.get("face_behavior", {})

    last_face_behavior_state = face_behavior_dict.get(str(len(face_behavior_dict)), {}).get("data", {})

    if (last_face_behavior_state != response_data):
        face_behavior = attempt.proctoring_data.get("face_behavior", {})

        # data_temp = data.copy()
        response_data["time"] = datetime.datetime.now().timestamp()

        face_behavior[len(face_behavior)] = response_data

        attempt.proctoring_data["face_behavior"] = face_behavior

    attempt.save()

    # print(response.json())
    # return JsonResponse(data)
    # return JsonResponse({"status": "ok"})


behavior_logger_func_mapping = {
    "tab" : __tab_behavior_logger,
    "face" : __face_behavior_detector,
}


@method_decorator(csrf_exempt, name='dispatch')
class Log(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            encoded_id = data.get('id', None)
            assert encoded_id is not None, 'Empty ID!'
            
            encoded_target = data.get('target', None)
            assert encoded_target is not None, 'Empty target!'

            type = data.get('type', None)
            assert type is not None, 'Empty type!'
            assert type in behavior_logger_func_mapping.keys(), 'Wrong type!'
                
            data = data.get('data', None)
            assert data is not None, 'Empty data!'

            encrypted_id = urlsafe_base64_decode(encoded_id)
            id = data_encryption.str_decrypt(encrypted_id)

            encrypted_target = urlsafe_base64_decode(encoded_target)
            target = data_encryption.str_decrypt(encrypted_target)

            behavior_logger_func_mapping[type](request, id, target, data)
            
            return JsonResponse({"status": "ok"})
        except AssertionError as error:
            return JsonResponse({"status": f'error: {error}'})