# agora-video-call
This README would normally document whatever steps are necessary to get your application up and running.

### Tech. used in the porject? ###

* Agora SDK
* Pusher
* python >=3.6
* Django

### How do I get set up? ###

* Clone the repo: ```git clone https://github.com/Sajzad/agora-video-call.git```.

* Install virtualenv on your system. For linux: ```pip install virtualenv```.

* Go to agora-video-call dir. And create virtual environment with virtualenv: ```virtualenv -p /usr/bin/python3 .env```.

* Activate the virtual environment: source ```.env/bin/activate```.

* Install required dependencies: ```pip install -r requirements.txt```.

* Set these environment variables which should be forwarded via email with corresponding values.

* Go to website dir where the manage.py file is.

* Create migrations files: ```./manage.py makemigrations```.

* Update the database with migrations: ```./manage.py migrate```.

* Start the local server: ```./manage.py runserver```.

* Server can be accessed from this link ```http://127.0.0.1:8000/```.

### How do I make video call? ###

* Create an account from this Sign Up link ```http://127.0.0.1:8000/signup``` and you will be redirected to Video chat room.

* Create another account from incognito mode. Now we will be able to see who is online and we can make a call. As soon as the call is acceped by the other end, video streaming will be initiated.

# I have attached few screen-shot here

1. Post signin you will be redirected to a chat room like below
![video_1](https://user-images.githubusercontent.com/42478821/148390664-9de7bad5-8393-4f6e-b4b0-9cbfeef93313.png)

2. After placing a call so somebody, a notification will be appeared at the receiver end like below. 

![video2](https://user-images.githubusercontent.com/42478821/148391161-9f12734f-0846-41ab-9e53-e8538e2226bb.png)

3. Upon accepted the request video streaming will be intiated and call can be controlled.

![video_chat](https://user-images.githubusercontent.com/42478821/148391325-08af9eb5-cdb6-4699-9c25-487d39f65b91.png)

Hope you enjoyed the project. Please feel free to contact me If require any further assistance
sajzadhasan@gmail.com


