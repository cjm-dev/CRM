from flask import Flask,render_template,request,session,redirect,url_for, json, jsonify, flash
from bson.objectid import ObjectId
from pymongo import MongoClient
from fabric.api import *
import bcrypt
import subprocess
 
from flask_socketio import SocketIO, emit, disconnect


application = Flask(__name__)

client = MongoClient('localhost:27017')
db = client.MachineData

async_mode = None
thread = None
socketio = SocketIO(application, async_mode=async_mode)

@application.route('/')
def index():
    if 'email' in session:
        admin_user = db.users.find_one()
        print admin_user
        #return'You are logged in as ' + session['email']
        return admin_user['title']
        #return render_template('dashboard.html')
    return render_template('index.html')

@application.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        admin_user = db.users.find_one({'email': request.form['email']})
        print admin_user
        # The user already exists
        if admin_user is None:
            print "here"
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            db.users.insert_one({'name': request.form['name'],'email': request.form['email'], 'password': hashpass})
            return redirect(url_for('index'))
        return "That email is already registered"
    return render_template('register.html')


@application.route('/login', methods=['POST'])
def login():
    admin_user = db.users.find_one({'email': request.form['email']})
    print "login here"
    if admin_user:
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), admin_user['password'].encode('utf-8')) == admin_user['password'].encode('utf-8'):
            session['email'] = request.form['email']
    #        print admin_user['name']
            #get_user(admin_user)
            return redirect(url_for('showMachineList'))
    #return 'Invalid Email or Password'
    flash("Invalid Credentials")
    return render_template('index.html')



@application.route('/logout', methods=['GET'])
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))

#@application.route('/dashboard', methods=['GET'])
#def dashboard():
#    if 'email' in session:
#        return render_template('dashboard.html')

#    return render_template('index.html')

## MACHINE DATA
##### CJM DONT FORGET THIS!!
@application.route('/dashboard', methods=['GET'])
def showMachineList():
    print "In showMachine"
    if 'email' in session:
        print "passed session"
        return render_template('list.html', async_mode=socketio.async_mode)
    else:
        return render_template('index.html')

@application.route("/addMachine", methods=['POST'])
def addMachine():
    try:
        json_data = request.json['info']
        deviceName = json_data['device']
        ipAddress = json_data['ip']
        userName = 'xxxx' 
        password = 'xxxx'
        portNumber = json_data['port']

        db.Machines.insert_one({
            'device': deviceName, 'ip': ipAddress, 'username': userName, 'password': password, 'port': portNumber
        })
        return jsonify(status='OK', message='inserted successfully')

    except Exception, e:
        return jsonify(status='ERROR', message=str(e))
'''
@application.route('/')
def showMachineList():
    return render_template('list.html')
'''


@application.route('/getMachine', methods=['POST'])
def getMachine():
    try:
        machineId = request.json['id']
        machine = db.Machines.find_one({'_id': ObjectId(machineId)})
        machineDetail = {
            'device': machine['device'],
            'ip': machine['ip'],
            'username': 'xxxx',
            'password': 'xxxx',
            'port': machine['port'],
            'id': str(machine['_id'])
        }
        return json.dumps(machineDetail)
    except Exception, e:
        return str(e)


@application.route('/updateMachine', methods=['POST'])
def updateMachine():
    try:
        machineInfo = request.json['info']
        machineId = machineInfo['id']
        device = machineInfo['device']
        ip = machineInfo['ip']
        username = 'xxxx'
        password = 'xxxx'
        port = machineInfo['port']

        db.Machines.update_one({'_id': ObjectId(machineId)}, {
            '$set': {'device': device, 'ip': ip, 'username': username, 'password': password, 'port': port}})
        return jsonify(status='OK', message='updated successfully')
    except Exception, e:
        return jsonify(status='ERROR', message=str(e))


@application.route("/getMachineList", methods=['POST'])
def getMachineList():
    try:
        machines = db.Machines.find()

        machineList = []
        for machine in machines:
            print machine
            machineItem = {
                'device': machine['device'],
                'ip': machine['ip'],
                'username': 'xxxx',
                'password': 'xxxx',
                'port': machine['port'],
                'id': str(machine['_id'])
            }
            machineList.append(machineItem)
    except Exception, e:
        return str(e)
    return json.dumps(machineList)


@application.route("/execute", methods=['POST'])
def execute():
    try:
        machineInfo = request.json['info']
        ip = machineInfo['ip']
        username = 'xxxx'
        password = 'xxxx'
        command = machineInfo['command']
        isRoot = machineInfo['isRoot']

        env.host_string = username + '@' + ip
        env.password = password
        resp = ''
        with settings(warn_only=True):
            if isRoot:
                resp = sudo(command)
            else:
                resp = run(command)

        return jsonify(status='OK', message=resp)
    except Exception, e:
        print 'Error is ' + str(e)
        return jsonify(status='ERROR', message=str(e))


@application.route("/deleteMachine", methods=['POST'])
def deleteMachine():
    try:
        machineId = request.json['id']
        db.Machines.remove({'_id': ObjectId(machineId)})
        return jsonify(status='OK', message='deletion successful')
    except Exception, e:
        return jsonify(status='ERROR', message=str(e))

@application.route("/findNodes", methods=['POST'])
def findNodes():
    try:
        ip = '10.0.2.6'
        username = 'xxxx'
        password = 'xxxx'
        isRoot = True
        command = 'arp-scan --interface=eth0 --localnet'
        env.host_string = username + '@' + ip
        env.password = password
        resp = ''
        with settings(warn_only=True):
            if isRoot:
                resp = sudo(command)
            else:
                resp = run(command)

        return jsonify(status='OK', message=resp)
    except Exception, e:
        print 'Error is ' + str(e)
        return jsonify(status='ERROR', message=str(e))

## SOCKET FUNCTIONS
def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(5)
        count += 1
        ip_list = ["10.0.2.6", "10.0.2.4", "10.0.2.5"]
        username = 'xxxx'
        password = 'xxxx'
        shell_path = "/home/xxxx/PythonFlaskRemoteApp-master/static/shell_files/"
        command = "/home/xxxx/PythonFlaskRemoteApp-master/static/shell_files/cpu_utilization.sh"
        command_list = ['cpu_utilization.sh', 'current_ram.sh', 'load_avg.sh' ]
        for x in range(0,3):
            if x == 0:
                type_val = 'A'
            elif x == 1:
                type_val = 'B'
            else:
                type_val = 'C'
            for j in range(0,3):
                env.host_string = username + '@' + ip_list[x]
                env.password = password
                resp = ''
                with settings(warn_only=True):
                    resp = run(shell_path+command_list[j])
                print "test=", resp
                socketio.emit('my_response',
                              {'data': str(resp), 'count': count, 'type': type_val, 'sub': 's'+str(j)},
                              namespace='/test')

@socketio.on('my_event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count']})

@socketio.on('disconnect_request', namespace='/test')
def disconnect_request():
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my_response',
         {'data': 'Disconnected!', 'count': session['receive_count']})
    disconnect()


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    if thread is None:
        thread = socketio.start_background_task(target=background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)

if __name__ == '__main__':
    application.secret_key = 'mysecret'
    application.run(debug=True)
    socketio.run(application, debug=True)
