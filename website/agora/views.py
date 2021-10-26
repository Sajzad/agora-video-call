import os
import time
import json, requests
import pyrebase

from django.http.response import JsonResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from .agora_key.RtcTokenBuilder import RtcTokenBuilder, Role_Attendee
from pusher import Pusher
 

from .models import Session


# /home/sajjad/Desktop/sv/django/agora
config = {
    "apiKey": "AIzaSyC-6M8is3lP1dAhbjLZujUDSJ7egiKMgK8",
    "authDomain": "agora-8783f.firebaseapp.com",
    "projectId": "agora-8783f",
    "storageBucket": "agora-8783f.appspot.com",
    "messagingSenderId": "822344920295",
    "appId": "1:822344920295:web:9224f2fd57cfd563854642",
    "databaseURL": "https://agora-8783f-default-rtdb.asia-southeast1.firebasedatabase.app",
    "measurementId": "G-LX5JC9VECY"    
}
# Initialising database,auth and firebase for further use
firebase=pyrebase.initialize_app(config)
authe = firebase.auth()
database=firebase.database()


def is_logged_in(func=None):
    def inner(request):
        if request.session:
            session_id = ""
            try:
                session_id = request.session['uid']
                print(session_id)
            except:
                pass
            if Session.objects.filter(session_id=session_id).exists():
                pass
            else:
                return redirect('agora:signin')
        else:
            return redirect('agora:signin')

    return inner

def chat(request):
    if request.session:
        session_id = ""
        all_users = ""
        try:
            session_id = request.session['uid']
            print(session_id)
        except:
            pass
        if Session.objects.filter(session_id=session_id).exists():
            User = get_user_model()
            all_users = User.objects.exclude(id=request.user.id).only('id', 'username')
        else:
            return redirect("agora:agora-index")
    else:
        return redirect("agora:agora-index")

    return render(request, 'video/chat.html', {'allUsers': all_users})

def init_pusher():
    """
    Instantiate a Pusher Client
    """
    pusher_client = Pusher(app_id=os.environ.get('PUSHER_APP_ID'),
                           key=os.environ.get('PUSHER_KEY'),
                           secret=os.environ.get('PUSHER_SECRET'),
                           ssl=True,
                           cluster=os.environ.get('PUSHER_CLUSTER')
                           )
    return pusher_client

def signin_view(request):
    if request.session:
        session_id = ""
        try:
            session_id = request.session['localId']
        except:
            pass
        if Session.objects.filter(session_id=session_id).exists():
            return redirect("agora:agora-index")

    err_message = ""
    if request.method == "POST":
        email = request.POST.get('email')
        pwd = request.POST.get('pwd')
        try:
            user=authe.sign_in_with_email_and_password(email,pwd)
            print(user)
            if user['localId']:
                Session.objects.create(session_id=user['localId'])
                request.session['uid'] = user['localId']
                return redirect("agora:agora-index")

        except requests.HTTPError as e:
            r = json.loads(e.args[1])
            err_message = r['error']['message']
            print(type(err_message))
            print(err_message)
        print(email, pwd)

    context = {

        "err_message":err_message
    }
    return render(request, 'signin.html', context)

def logout_view(request):
    try:
        Session.objects.filter(session_id=request.session['uid']).delete()
        del request.session['uid']
    except:
        pass
    return redirect("agora:signin")

    return render(request, "signin.html")

def signup_view(request):
    context = {
    
    }
    return render(request, 'signup.html', context)

@csrf_exempt
def pusher_auth(request):
    pusher_client = init_pusher()
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

    appID = os.environ.get("AGORA_APP_ID")    
    appCertificate = os.environ.get("AGORA_CERTIFICATE") 

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
    pusher_client = init_pusher()
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

def trigger_event(request):
    data = json.loads(request.body)
    check = data['check']
    pusher_client = init_pusher()
    if check == "decline":
        pusher_client.trigger(
            'presence-online-channel',
            'decline',
            {
                'userToCall': "",
                'channelName': "",
                'from': ""
            }
        )
    context = {

    }
    return JsonResponse(status=200, data=context)