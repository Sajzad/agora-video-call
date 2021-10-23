import os
import time
import json

from django.http.response import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .agora_key.RtcTokenBuilder import RtcTokenBuilder, Role_Attendee
from pusher import Pusher


# pusher creds
# app_id = "1286296"
# key = "14a70f173fd63bd6827c"
# secret = "35c7801fc2a23452161e"
# cluster = "ap1"


# Instantiate a Pusher Client
pusher_client = Pusher(app_id = "1286296",
                       key = "14a70f173fd63bd6827c",
                       secret = "35c7801fc2a23452161e",
                       ssl = False,
                       cluster = "ap1",
                       )

# pusher_client = Pusher(app_id=os.environ.get('PUSHER_APP_ID'),
#                        key=os.environ.get('PUSHER_KEY'),
#                        secret=os.environ.get('PUSHER_SECRET'),
#                        ssl=True,
#                        cluster=os.environ.get('PUSHER_CLUSTER')
#                        )


@login_required(login_url='/admin/')

def chat(request):
    User = get_user_model()
    all_users = User.objects.exclude(id=request.user.id).only('id', 'username')
    return render(request, 'video/chat.html', {'allUsers': all_users})

@csrf_exempt
def pusher_auth(request):
    print(request.POST)
    payload = pusher_client.authenticate(
        channel=request.POST['channel_name'],
        socket_id=request.POST['socket_id'],
        custom_data={
            'user_id': request.user.id,
            'user_info': {
                'id': request.user.id,
                'name': request.user.username
            }
        })
    print(payload)
    return JsonResponse(payload)


def generate_agora_token(request):
    print("agora token")

    appID = "bdedc9be41ee4f14b79c9cdc80fe86d6"     
    appCertificate = "276fbee9a94c41e29f43a9169aafc972"  

    # appID = os.environ.get('AGORA_APP_ID')
    # appCertificate = os.environ.get('AGORA_APP_CERTIFICATE')

    channelName = json.loads(request.body.decode(
        'utf-8'))['channelName']
    userAccount = request.user.username
    expireTimeInSeconds = 3600
    currentTimestamp = int(time.time())
    privilegeExpiredTs = currentTimestamp + expireTimeInSeconds

    token = RtcTokenBuilder.buildTokenWithAccount(
        appID, appCertificate, channelName, userAccount, Role_Attendee, privilegeExpiredTs)

    return JsonResponse({'token': token, 'appID': appID})


def call_user(request):
    body = json.loads(request.body.decode('utf-8'))
    print(body)
    user_to_call = body['user_to_call']
    channel_name = body['channel_name']
    caller = request.user.id

    pusher_client.trigger(
        'presence-online-channel',
        'make-agora-call',
        {
            'userToCall': user_to_call,
            'channelName': channel_name,
            'from': caller
        }
    )
    return JsonResponse({'message': 'call has been placed'})