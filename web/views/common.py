import hashlib

from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from api.models import UserToken

from .teacher import teacher_list
from .student import student_index
from common.utils import is_teacher
from api.backends import hash_token

@login_required()
def index(request):
    if is_teacher(request.user):
        return teacher_list(request, teacher__pk=request.user.id)
    return student_index(request)

@login_required()
def api_token(request):
    data = {
        "base_url": f"{request.scheme}://{request.META.get('HTTP_HOST', 'localhost:8000')}",
        "doc_token": "YOUR_TOKEN",
    }
    if request.method == 'POST':
        token_plaintext = get_random_string(32)
        token_secure = hash_token(token_plaintext)

        try:
            token = UserToken.objects.get(user__id=request.user.id)
            token.token = token_secure
            token.save()
        except UserToken.DoesNotExist:
            token = UserToken()
            token.user = request.user
            token.token = token_secure
            token.save()

        data['token_plaintext'] = token_plaintext
        data['doc_token'] = token_plaintext

    return render(request, 'web/common/api_token.html', data)


def template_context(request):
    return {
        'is_teacher': is_teacher(request.user),
    }
