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
 
from .models import User



def init_firebase():
    """
        Initialize Firebase with config credentials.
    """
    config = {
        "apiKey": os.environ.get("FIREBASE_API_KEY"),
        "authDomain": os.environ.get("FIREBASE_AUTH_DOMAIN"),
        "projectId": os.environ.get("FIREBASE_PROJECT_ID"),
        "storageBucket": os.environ.get("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.environ.get("FIREBASE_SENDER_ID"),
        "appId": os.environ.get("FIREBASE_APP_ID"),
        "databaseURL": os.environ.get("FIREBASE_DATABASE_URL"),
        # "measurementId": os.environ.get("FIREBASE_MEASUREMENT_ID")    
    }
    # Initialising database,auth and firebase for further use

    return pyrebase.initialize_app(config)
# database=firebase.database()

def chat(request):
    """
        Chat room views upon logged in.
        local vars:
            users: reponsible for all registered memebered for the chatroom.
    """
    # to make sure user is logged in
    if request.session:
        session_id = ""
        users = ""
        try:
            session_id = request.session['uid']
        except:
            pass
        if session_id:
            users = User.objects.exclude(user=request.session['user'])
            user = User.objects.get(user=request.session['user'])
        else:
            return redirect("agora:signin")
    else:
        return redirect("agora:signin")

    context = {
        "users": users,
        "user" : user
    }

    return render(request, 'video/chat.html', context)

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
    """
        Signin view which will take email and password for authentication with Firebase. On successful authentication, user will be
        redirected to chat room.
    """
    err_message = ""

    if request.session:
        session_id = ""
        try:
            session_id = request.session['localId']
        except:
            pass
        if session_id:
            return redirect("agora:agora-index")

    if request.method == "POST":
        email = request.POST.get('email')
        pwd = request.POST.get('pwd')
        try:
            authe = init_firebase().auth()
            user = authe.sign_in_with_email_and_password(email,pwd)
            if user['localId']:
                request.session['uid'] = user['localId']
                user = User.objects.filter(email__contains = email)[0].user
                request.session['user'] = user
                return redirect("agora:agora-index")

        except requests.HTTPError as e:
            r = json.loads(e.args[1])
            err_message = r['error']['message']

    context = {

        "err_message":err_message
    }
    return render(request, 'signin.html', context)

def logout_view(request):
    """
        Session_key will be deleted upon log out request.
    """
    try:
        del request.session['uid']
        del request.session['user']
    except:
        pass
    return redirect("agora:signin")

    return render(request, "signin.html")

def signup_view(request):

    err_message = ''

    if request.method == "POST":
        user = request.POST.get("username")
        email = request.POST.get("email")
        pwd1 = request.POST.get("pwd1")
        pwd2 = request.POST.get("pwd2")
        if pwd1 != pwd2:
            err_message = "Password doesn't match"
        elif User.objects.filter(user=user).exists():
            err_message = "User already exists!"        
        elif User.objects.filter(email=email).exists():
            err_message = "Email already exists!"
        else:
            try:
                authe = init_firebase().auth()
                auth=authe.create_user_with_email_and_password(email,pwd1)
            except Exception as e:
                print(e)
                print(dir(e))
            User.objects.create(user=user, email=email)
            request.session['uid'] = auth['localId']
            request.session['user'] = user
            return redirect("agora:agora-index")

        print(user, email, pwd2, pwd1)

    context = {
        "err_message":err_message
    }
    return render(request, 'signup.html', context)

@csrf_exempt
def pusher_auth(request):
    pusher_client = init_pusher()
    user = User.objects.filter(user=request.session['user'])[0]
    payload = pusher_client.authenticate(
        channel=request.POST['channel_name'],
        socket_id=request.POST['socket_id'],
        custom_data={
            'user_id': user.id,
            'user_info': {
                'id': user.id,
                'name': user.user
            }
        })
    return JsonResponse(payload)


def generate_agora_token(request):

    appID = os.environ.get("AGORA_APP_ID")    
    appCertificate = os.environ.get("AGORA_CERTIFICATE") 

    channelName = json.loads(request.body.decode('utf-8'))['channelName']
    userAccount = request.session['user']
    expireTimeInSeconds = 3600
    currentTimestamp = int(time.time())
    privilegeExpiredTs = currentTimestamp + expireTimeInSeconds

    token = RtcTokenBuilder.buildTokenWithAccount(
        appID, appCertificate, channelName, userAccount, Role_Attendee, privilegeExpiredTs)

    return JsonResponse({'token': token, 'appID': appID})


def call_user(request):
    """
        Placing call requests to the other with websocket and creating a presence channel using pusher so that any event during 
        video call can be triggered in real time.
    """
    body = json.loads(request.body.decode('utf-8'))
    user_to_call = body['user_to_call']
    channel_name = body['channel_name']
    caller = request.session['user']
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
    """
        To trigger a decline event to the presence channel to stop streaming on declining call or ending call.
    """
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