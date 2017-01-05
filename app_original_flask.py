from flask import Flask,render_template,jsonify,json,request,session,redirect,url_for,flash
from pymongo import MongoClient
from bson.objectid import ObjectId
from fabric.api import *
import bcrypt

application = Flask(__name__)

client = MongoClient('localhost:27017')
db = client.MachineData

### LOGIN/REGe
@application.route('/')
def index():
    if 'email' in session:
        admin_user = db.users.find_one()
        print admin_user

        return admin_user['name']

    return render_template('index.html')

@application.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        admin_user = db.users.find_one({'email': request.form['email']})
        print admin_user
        # The user already exists
        if admin_user is None:
            print "here in reg"
            hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            db.users.insert_one({'name': request.form['name'],'email': request.form['email'], 'password': hashpass})
            return redirect(url_for('index'))
        return "That email is already registered"
    return render_template('register.html')

@application.route('/login', methods=['POST'])
def login():
    admin_user = db.users.find_one({'email': request.form['email']})
    print "login here", admin_user,
    if admin_user:
        print "admin user2996", bcrypt.hashpw(request.form['password'].encode('utf-8'), admin_user['password'].encode('utf-8'))
        if bcrypt.hashpw(request.form['password'].encode('utf-8'), admin_user['password'].encode('utf-8')) == admin_user['password'].encode('utf-8'):
            print "passed",request.form['email']
            session['email'] = request.form['email']
            print "passed2", session['email']
            return redirect(url_for('showMachineList'))
        else:
            print "error2"
    #return 'Invalid Email or Password'
    print "error"
    flash("Invalid Credentials")
    return redirect(url_for('index'))

@application.route('/logout', methods=['GET'])
def logout():
    session.pop('email', None)

### MACHINE DATA
@application.route("/addMachine",methods=['POST'])
def addMachine():
    try:
        json_data = request.json['info']
        deviceName = json_data['device']
        ipAddress = json_data['ip']
        userName = json_data['username']
        password = json_data['password']
        portNumber = json_data['port']

        db.Machines.insert_one({
            'device':deviceName,'ip':ipAddress,'username':userName,'password':password,'port':portNumber
            })
        return jsonify(status='OK',message='inserted successfully')

    except Exception,e:
        return jsonify(status='ERROR',message=str(e))

##### CJM DONT FORGET THIS!!
@application.route('/dashboard', methods=['GET'])
def showMachineList():
    print "In showMachine"
    if 'email' in session:
        print "passed session"
        return render_template('list.html')
    else:
        return render_template('index.html')
'''
@application.route('/')
def showMachineList():
    return render_template('list.html')
'''
@application.route('/getMachine',methods=['POST'])
def getMachine():
    try:
        machineId = request.json['id']
        machine = db.Machines.find_one({'_id':ObjectId(machineId)})
        machineDetail = {
                'device':machine['device'],
                'ip':machine['ip'],
                'username':machine['username'],
                'password':machine['password'],
                'port':machine['port'],
                'id':str(machine['_id'])
                }
        return json.dumps(machineDetail)
    except Exception, e:
        return str(e)

@application.route('/updateMachine',methods=['POST'])
def updateMachine():
    try:
        machineInfo = request.json['info']
        machineId = machineInfo['id']
        device = machineInfo['device']
        ip = machineInfo['ip']
        username = machineInfo['username']
        password = machineInfo['password']
        port = machineInfo['port']

        db.Machines.update_one({'_id':ObjectId(machineId)},{'$set':{'device':device,'ip':ip,'username':username,'password':password,'port':port}})
        return jsonify(status='OK',message='updated successfully')
    except Exception, e:
        return jsonify(status='ERROR',message=str(e))

@application.route("/getMachineList",methods=['POST'])
def getMachineList():
    try:
        machines = db.Machines.find()
        
        machineList = []
        for machine in machines:
            print machine
            machineItem = {
                    'device':machine['device'],
                    'ip':machine['ip'],
                    'username':machine['username'],
                    'password':machine['password'],
                    'port':machine['port'],
                    'id': str(machine['_id'])
                    }
            machineList.append(machineItem)
    except Exception,e:
        return str(e)
    return json.dumps(machineList)

@application.route("/execute",methods=['POST'])
def execute():
    try:
        machineInfo = request.json['info']
        ip = machineInfo['ip']
        username = machineInfo['username']
        password = machineInfo['password']
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

        return jsonify(status='OK',message=resp)
    except Exception, e:
        print 'Error is ' + str(e)
        return jsonify(status='ERROR',message=str(e))

@application.route("/deleteMachine",methods=['POST'])
def deleteMachine():
    try:
        machineId = request.json['id']
        db.Machines.remove({'_id':ObjectId(machineId)})
        return jsonify(status='OK',message='deletion successful')
    except Exception, e:
        return jsonify(status='ERROR',message=str(e))


if __name__ == "__main__":
    application.run(host='0.0.0.0')

