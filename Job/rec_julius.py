# coding: UTF-8
import subprocess
import socket
import os
import re
import datetime
import numpy as np
import requests
import time
import glob
import multiprocessing as mp
import configparser
from argparse import ArgumentParser

NGwords = ['試験', 'テスト']
setting = configparser.ConfigParser()
setting.read('rec.conf','utf-8')
host = setting.get('shell','host')
port = int(setting.get('shell','port'))
url = setting.get('server','url')
recordsdir = setting.get('recognition','recordsdir')
engine = setting.get('recognition','engine')
span = setting.get('recognition','span')
limit = int(setting.get('recognition','limit'))
threshold = float(setting.get('recognition','threshold'))

def up2server():
    uplist = [r.split('/')[-1] for r in glob.glob(recordsdir+'/*')]
    files = {}
    for f in uplist:
        if 'wav' in f:
            files[f] = (f, open(recordsdir+'/'+f,'rb'),'audio/wav')
        elif 'txt' in f:
            files[f] = (f,open(recordsdir+'/'+f,'rb'),'text/plain')
        
    requests.post(url, files=files)
    


def recording(recfile, tmpfiles, cnt, mac):
    while True:
        now = datetime.datetime.now() # time starting record
        now = now.strftime('%Y%m%d%H%M%S')
        recfile['wav'] = recordsdir+'/record_{}.wav'.format(now)
        recfile['txt'] = re.sub('wav','txt',recfile['wav'])

        # raspberry pi
        if mac:
            args = ['rec', '--encoding', 'signed-integer', '--bits', '16', '--rate', '44100', recfile['wav'], 'trim', '0', span]
        else:
            args = ['arecord', '-d', span, '-D' 'plughw:2,0', '-f', 'cd','--buffer-size=100000', recfile['wav']]
        
        print('◉  Recording start ! > {}   '.format(recfile['wav']))
        tmpfiles.append(recfile['wav'])
        subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if cnt.value!=-1:
            cnt.value += 1
        if cnt.value>=limit:
            up2server()
            cnt.value = -1
        
        while len(tmpfiles)>limit:
            os.remove(tmpfiles[0])
            try:
                os.remove(re.sub('wav','txt',tmpfiles[0]))
            except:
                pass
            del tmpfiles[0]

def start_julius(model, view):
    subprocess.run(["pkill","-9","julius"])
    print('Model:{}'.format(model))
    engine = './julius-script/'+model+'.sh'
    if view:
        p = subprocess.Popen([engine],shell=True)
    else:
        p = subprocess.Popen([engine], stdout=subprocess.PIPE, shell=True)
    print('Start up julius')
    time.sleep(10)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    p.wait()
    # retry to start-up julius, take time
    while True:
        try:
            sock.connect((host,port))
        except:
            print('Connecting...')
            time.sleep(15)
        else:
            print('connected(⌒▽⌒)')
            break
    return p, sock
    

def recognition_julius(sock):
    silence = ['silE','silB','[s]','[/s]']
    data = ""
    while(data.find("\n.")==-1):
        add = str(sock.recv(1024).decode('utf-8'))
        data += add

    result = []
    cms = []
    if 'ERREXIT' in data:
        print(' ▶︎ ERROR !')
        #pass

    elif 'LISTEN' in data:
        print(' ▷ Ready')
        #pass

    elif 'REJECTED' in data:
        print(' ▶︎ REJECTED !')
        #pass

    elif 'STARTRECOG' in data:
        print(' ▷ Analyzing...')

    elif '</RECOGOUT>\n.' in data:        
        for line in data.split('\n'):
            index = line.find('WORD="')
            cmidx = line.find('CM="')
            if index!=-1:
                word = line[index+6:line.find('" ',index+6)]
                w = re.search('.+',word)
                if w!=None and w.group() not in silence:
                    cm = float(line[cmidx+4:line.find('"',cmidx+4)])
                    cms.append(cm)
                    word = w.group()
                    result.append(word)

    return result, cms # detected sentence[words list], confidence for each word

def detection(recfile, cnt, model, view):
    p, sock = start_julius(model, view)
    while True:
        result, cms = recognition_julius(sock)
        if len(result)!=0:
            sentence = ''.join(result)
            with open(recfile['txt'],'a') as f:
                print(sentence, file=f)
            print(sentence)
            for (res,c) in zip(result,cms):
                if res in NGwords and c>threshold:
                    print(' [!]   This will be on test   [!]')
                    up2server()
                    cnt.value = 0

    sock.close()

if __name__ == '__main__':
    pid = os.getpid()
    parser = ArgumentParser()
    parser.add_argument('-m', '--mac', action='store_true')
    parser.add_argument('-d', '--dic', default='dictation', choices=['dictation','lsr','ssr','grammar'])
    parser.add_argument('-v', '--view', action='store_true')
    args = parser.parse_args()
    with mp.Manager() as manager:
        recfile = manager.dict()
        tmpfiles = manager.list()
        tmpfiles += glob.glob('./records/*.wav')
        tmpfiles.sort()
        cnt = manager.Value('i',-1)
        p1 = mp.Process(target=recording, args=(recfile,tmpfiles,cnt,args.mac, ))
        p2 = mp.Process(target=detection, args=(recfile,cnt,args.dic,args.view,))
        p1.start()
        p2.start()
        p2.join()
        p1.terminate()
        print('おしまい')

