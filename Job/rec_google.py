# coding: UTF-8
import subprocess
import os
import re
import datetime
import numpy as np
import requests
import time
import glob
import multiprocessing as mp
from argparse import ArgumentParser
import speech_recognition as sr
import pyaudio

detect_words = ['テスト', '試験']
url = 'http://127.0.0.1:5000'
recordsdir = 'records'
span = '60'
limit = 3

def up2server():
    uplist = [r.split('/')[-1] for r in glob.glob(recordsdir+'/*')]
    files = {}
    for f in uplist:
        if 'wav' in f:
            files[f] = (f, open(recordsdir+'/'+f,'rb'),'audio/wav')
        elif 'txt' in f:
            files[f] = (f,open(recordsdir+'/'+f,'rb'),'text/plain')
    
    prev = time.time()
    requests.post(url, files=files)
    print('* Upload completed')
    print('* Required time: {}s'.format(time.time()-prev))

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


def recognition_google(r, source):
    r.adjust_for_ambient_noise(source)
    print("\r▷ Ready ... ", end="")
    audio = r.listen(source)
    print('▷ Finish')
    prev = time.time()
    try:
        result = r.recognize_google(audio, language='ja-JP')
        print('* Processing time: {}s'.format(time.time()-prev))
    except:
        result = ''

    return result


def detection(recfile, cnt):

    r = sr.Recognizer()
    mic = sr.Microphone()
    
    with mic as source:
        while(True):
            result = recognition_google(r, source)
            # print(result)
            if len(result)!=0:
                with open(recfile['txt'], 'a') as f:
                    print(result, file=f)
                for w in detect_words:
                    if w in result:
                        print('[!]   This will be on your exam   [!]')
                        up2server()
                        cnt.value = 0


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-m', '--mac', action='store_true')
    args = parser.parse_args()

    with mp.Manager() as manager:
        recfile = manager.dict()
        tmpfiles = manager.list()
        tmpfiles += glob.glob('./records/*.wav')
        tmpfiles.sort()
        cnt = manager.Value('i',-1)
        p1 = mp.Process(target=recording, args=(recfile,tmpfiles,cnt,args.mac, ))
        p2 = mp.Process(target=detection, args=(recfile,cnt,))
        p1.start()
        p2.start()
        p2.join()
        p1.terminate()
        print('おしまい')