#!flask/bin/python
from flask import Flask, jsonify,request
from flask import abort
from flask import make_response
from flask import url_for
from flask_httpauth import HTTPBasicAuth
import logging
from configparser import ConfigParser
import requests
auth = HTTPBasicAuth()
app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'alarm': u'a1',
        'description': u'alarm1', 
        'done': False
    },
    {
        'id': 2,
        'alarm': u'a2',
        'description': u'alarm2', 
        'done': False
    }
]
def telegram_bot_sendtext(bot_message):

   
   bot_token = '999999999:AAaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
   bot_chatID = 'ddddddd'
   send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
  # send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&text=' + bot_message
  
    #https://api.telegram.org/bot996303276:AAGzG4KOztClAl2jbjG99BPSh3QzSANW9Lw/getUpdates
   response = requests.get(send_text)
   print(send_text)
   return response.json()
    
#With the authentication system setup, all that is left is to indicate which functions need to be protected, by adding the @auth.login_required decorator.

@auth.get_password
def get_password(username):
    if username == 'miguel':
        return 'python'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 401)


#Instead of returning task ids we can return the full URI that controls the task, so that clients get the URIs ready to be used. For this we can write a small helper function that generates a "public" version of a task to send to the client:

def make_public_task(task):
    new_task = {}
    for field in task:
        if field == 'id':
            new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
        else:
            new_task[field] = task[field]
    return new_task

#For the update_task function we are trying to prevent bugs by doing exhaustive checking of the input arguments. We need to make sure that anything that the client provided us is in the expected format before we incorporate it into our database.
#$ curl -i -H "Content-Type: application/json" -X PUT -d '{"done":true}' http://localhost:5000/mgateway/v1.0/tasks/2

@app.route('/mgateway/v1.0/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'alarm' in request.json and type(request.json['alarm']) != unicode:
        abort(400)
    if 'description' in request.json and type(request.json['description']) is not unicode:
        abort(400)
    if 'done' in request.json and type(request.json['done']) is not bool:
        abort(400)
    task[0]['alarm'] = request.json.get('alarm', task[0]['alarm'])
    task[0]['description'] = request.json.get('description', task[0]['description'])
    task[0]['done'] = request.json.get('done', task[0]['done'])
    return jsonify({'task': task[0]})

@app.route('/mgateway/v1.0/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    tasks.remove(task[0])
    return jsonify({'result': True})

#$ curl -i -H "Content-Type: application/json" -X POST -d '{"alarm":"Read a book"}' http://localhost:5000/mgateway/v1.0/tasks

@app.route('/mgateway/v1.0/tasks', methods=['POST'])
def create_task():
    if not request.json or not 'alarm' in request.json:
        abort(400)
    if tasks[-1]['id']<1000:
        task = {
            'id': tasks[-1]['id'] + 1,
            'alarm': request.json['alarm'],
            'description': request.json.get('description', ""),
            'done': False
        }
    else:
        task = {
            'id': tasks[0]['id'] ,
            'alarm': request.json['alarm'],
            'description': request.json.get('description', ""),
            'done': False

        } 
    #print(task)
    test = telegram_bot_sendtext(request.json['alarm'])
    tasks.append(task)
    return jsonify({'task': task}), 201
@app.route('/mgateway/v1.0/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = [task for task in tasks if task['id'] == task_id]
    if len(task) == 0:
        abort(404)
    return jsonify({'task': task[0]})



#All we are doing here is taking a task from our database and creating a new task that has all the fields except id, which gets replaced with another field called uri, generated with Flask's url_for.

@app.route('/mgateway/v1.0/tasks', methods=['GET'])
#@auth.login_required
def get_tasks():
    return jsonify({'tasks': [make_public_task(task) for task in tasks]})


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

#para evitar mostrar un cuadro de diálogo de inicio de sesion al suceder el error 401,
# se recurre a cambiar 401 por 403
@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)


if __name__ == '__main__':
    app.run(debug=True)
