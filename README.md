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
# register user
curl -X POST http://127.0.0.1:8000/accounts/register --data 'email=josep3@udg.edu&password=alpine123&password2=alpine123'
# login user
curl -X POST http://127.0.0.1:8000/accounts/login --data 'username=josep3@udg.edu&password=alpine123'
# recover user token
curl -X POST http://127.0.0.1:8000/api-token-auth --data 'username=josep3@udg.edu&password=alpine123'

# acces protected view (de moment, no funciona)
http -a josep3@udg.edu:alpine123 curl -X GET http://127.0.0.1:8000/photos/ -H 'Authorization: Token 2724719c8b369d6a249864eb2664a08546aa08e3'
http  http://127.0.0.1:8000/photos/ 'Authorization: Token e49e4f2f7ee1f950d5ee4d56fede373d1e1c61eb'
