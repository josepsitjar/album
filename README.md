# Django Project

### Install the dependencies

pip install -r requirements.txt

### Django rest framework

Endpoint API with filter using django_filter

Example url based on id:
http://127.0.0.1:8000/photos/?format=json&id=1


### Token Based Authentication with Django, Vue and Axios

### User administration

Curl example:
curl -X POST http://127.0.0.1:8000/accounts/register --data 'email=josep3@udg.edu&password=alpine123&password2=alpine123'
curl -X POST http://127.0.0.1:8000/accounts/login --data 'username=josep3@udg.edu&password=alpine123'
