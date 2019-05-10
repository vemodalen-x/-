import collections
import contextlib
import sys
import wave
from aip import AipSpeech
from pydub import AudioSegment
import pydub
import datetime
import os
import time
import io
import webrtcvad
import http.client
import hashlib
import urllib.request
import random
import requests
import base64
import json


#输入的单词
def baidu_translate(q,fromLang,toLang):
#q="我是12345"
#输入中文输出英文
    appid = '20190309000275491' #你的appid
    secretKey = '3X_lrZchAlZit8LeHVl2' #你的密钥
    httpClient = None
    myurl = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
    #fromLang = 'zh'中文 auto 自动识别 kor韩语
    #toLang = 'en'英文    jp 日语 fra法语等 详见http://api.fanyi.baidu.com/api/trans/product/apidoc
    salt = random.randint(32768, 65536)
    sign = appid+q+str(salt)+secretKey#拼接字符串
    m1 = hashlib.new('md5')#python3没有md5
    m1.update(sign.encode('utf-8'))
    sign=m1.hexdigest()
    myurl = myurl+'?q='+urllib.request.quote(q)+'&from='+fromLang+'&to='+toLang+'&appid='+appid+'&salt='+str(salt)+'&sign='+sign
    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)
        #response是HTTPResponse对象
        response = httpClient.getresponse()
        result=response.read()  
        data = json.loads(result)
        wordMean=data['trans_result'][0]['dst']
        return(wordMean)
    except Exception as e:
        return ""
    finally:
        if httpClient:
            httpClient.close()

def xunfei_translate(word,fromlang,tolang):
   
    if(fromlang=='zh'):
        FROM ='cn'
    else:
        FROM=fromlang
    if(tolang=='zh'):
        to='cn'
    else:
        to = tolang
    q = word
    url = 'http://openapi.openspeech.cn'
    app_id = '5caea3f5'
    api_key = 'b2c4f23fdad7fe1683e06f3f4c8aa1c1'

    x_param = base64.b64encode(('appid={0}'.format(app_id)).encode('utf-8'))
    x_par = str(x_param, 'utf-8')
    # print(x_param)
    m2 = hashlib.md5()
    m2.update((q + str(x_param, 'utf-8') + api_key).encode('utf-8'))
    sign = m2.hexdigest()
    # print((q + str(x_param, 'utf-8') + api_key))
    # print(sign)
    header = {
        'X-Par': x_par,
        'Ver': '1.0',
    }

    res = requests.get(url= url + '/webapi/its.do?svc=its&token=its&from={0}&to={1}&q={2}&sign={3}'.format(FROM, to, q, sign), headers=header)
    temp=str(base64.decodebytes(res.content),'utf-8')
    results=json.loads(temp)
    return results['trans_result']['dst']

""" baidu 你的 APPID AK SK """
APP_ID = '14345689'
API_KEY = 'uuhDspKiyziHu3TqTRex90fj'
SECRET_KEY = 'dNCt4xw8OGL0HPS2zNU34mwf80NtP4r9'
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
"""xunfei 普通话(sms16k),普通话(sms8k),英语(sms-en8k),英语(sms-en16k)"""
URL = "http://api.xfyun.cn/v1/service/v1/iat"
x_APPID = "5caea3f5"
x_API_KEY = "b2dc36c825fe919242e4011a3d6b6e6e"

def getHeader(aue, engineType):
    curTime = str(int(time.time()))
    # curTime = '1526542623'
    param = "{\"aue\":\"" + aue + "\"" + ",\"engine_type\":\"" + engineType + "\"}"
    #print("param:{}".format(param))
    paramBase64 = str(base64.b64encode(param.encode('utf-8')), 'utf-8')
    #print("x_param:{}".format(paramBase64))

    m2 = hashlib.md5()
    m2.update((x_API_KEY + curTime + paramBase64).encode('utf-8'))
    checkSum = m2.hexdigest()
    #print('checkSum:{}'.format(checkSum))
    header = {
        'X-CurTime': curTime,
        'X-Param': paramBase64,
        'X-Appid': x_APPID,
        'X-CheckSum': checkSum,
        'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
    }
    #print(header)
    return header
def getBody(filepath):
    binfile = open(filepath, 'rb')
    data = {'audio': base64.b64encode(binfile.read())}
    #print(data)
    #print('data:{}'.format(type(data['audio'])))
    # print("type(data['audio']):{}".format(type(data['audio'])))
    return data
def xunfei_recognition(path,fromlang):
    aue = "raw"
    if(fromlang=='zh'):
        engineType = "sms16k"
    elif(fromlang=='en'):
        engineType="sms-en16k"
    audioFilePath = path
    r = (requests.post(URL, headers=getHeader(aue, engineType), data=getBody(audioFilePath))).content.decode('utf-8')
    result=json.loads(r)
    return result['data']

def get_time(time_second):
    hour=int(time_second/3600)
    minute=int((time_second-hour*3600)/60)
    second=int(time_second-hour*3600-minute*60)
    st='{mhour}:{mminute}:{msecond}'.format(mhour=hour,mminute=minute,msecond=second)
    print(st)
    return st

def get_file_content(filepath):
    with open(filepath, 'rb') as fp:
        return fp.read()

def read_wave(path):
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        '''
        读取.wav文件。
        采取路径，并返回（PCM音频数据，采样率）。
        '''
        num_channels = wf.getnchannels()#声道数
        assert num_channels == 1
        sample_width = wf.getsampwidth()#量化位数（byte单位）
        assert sample_width == 2
        sample_rate = wf.getframerate()#采样频率
        assert sample_rate in (8000, 16000, 32000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate#返回声音数据和采样点数
#readframes：读取声音数据，传递一个参数指定需要读取的长度（以取样点为单位），readframes返回的是二进制数据（一大堆
#bytes)，在Python中用字符串表示二进制数据： 

def write_wave(path, audio, sample_rate):
    '''
    写一个.wav文件。
     获取路径，PCM音频数据和采样率。
    '''
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)#声道数1
        wf.setsampwidth(2)#量化位数2
        wf.setframerate(16000)#采样频率sample_rate
        wf.writeframes(audio)#写入声音数据audio
 

class Frame(object):
    def __init__(self, bytes, timestamp, duration):
        '''
        表示音频数据的“帧”。
        '''
        self.bytes = bytes#字节数
        self.timestamp = timestamp#时间戳
        self.duration = duration#持续时间
 

def frame_generator(frame_duration_ms, audio, sample_rate):
    '''
    从PCM音频数据audio生成音频帧。
     采用所需的帧持续时间（以毫秒为单位）frame_duration_ms，PCM数据audio和采样率sample_rate。
     产生所请求持续时间的帧。
    '''
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n
 
 
def vad_collector(sample_rate, frame_duration_ms,
                  padding_duration_ms, vad, frames):
    '''
    过滤掉非浊音音频帧。
    给定webrtcvad.Vad和音频帧源，仅产生
    浊音。
    在音频帧上使用填充的滑动窗口算法。
    当窗口中90％以上的帧都是浊音时（如
    由VAD报道，收集器触发并开始产生
    音频帧。然后收集器等待直到90％的帧
    这个窗口是清音的。
    窗户在正面和背面都有衬垫，以提供一个小窗户
    沉默的数量或围绕着的言论的开始/结束
    浊音帧。
    参数：
    sample_rate  - 音频采样率，单位为Hz。
    frame_duration_ms  - 帧持续时间（以毫秒为单位）。
    padding_duration_ms  - 填充窗口的数量，以毫秒为单位。
    vad  -  webrtcvad.Vad的一个实例。
    帧 - 音频帧的源（序列或发生器）。
    返回：生成PCM音频数据的生成器。
    '''
    f =open("f.txt","w")
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False
    voiced_frames = []
    for frame in frames:
        sys.stdout.write(
            '1' if vad.is_speech(frame.bytes, sample_rate) else '0')
        #f.write('1' if vad.is_speech(frame.bytes, sample_rate) else '0')
        if not triggered:
            ring_buffer.append(frame)
            num_voiced = len([f for f in ring_buffer
                              if vad.is_speech(f.bytes, sample_rate)])
            if num_voiced > 0.9 * ring_buffer.maxlen:
                sys.stdout.write('+(%s)' % (ring_buffer[0].timestamp,))
                time=ring_buffer[0].timestamp
                hour =int(time/3600)
                minute=int(time/60%60)
                sec=int(time%60)
                f.write('%d:%d:%d '%(hour,minute,sec))
                triggered = True
                voiced_frames.extend(ring_buffer)
                ring_buffer.clear()
        else:
            voiced_frames.append(frame)
            ring_buffer.append(frame)
            num_unvoiced = len([f for f in ring_buffer
                                if not vad.is_speech(f.bytes, sample_rate)])
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
                time=frame.timestamp + frame.duration
                hour =int(time/3600)
                minute=int(time/60%60)
                sec=int(time%60)
                f.write('%d:%d:%d '%(hour,minute,sec))
                f.write('\n')
                triggered = False
                yield b''.join([f.bytes for f in voiced_frames])
                ring_buffer.clear()
                voiced_frames = []
    if triggered:
        sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
        f.write('%.2f' % (frame.timestamp + frame.duration))
    sys.stdout.write('\n')
    if voiced_frames:
        yield b''.join([f.bytes for f in voiced_frames])
 
 
def main(argv): #第一个源语言 第二个目标语言
    '''
    if len(args) != 2:
        sys.stderr.write(
            'Usage: example.py <aggressiveness> <path to wav file>\n')
        sys.exit(1)
    '''
    audio, sample_rate = read_wave(r"./input.wav")#声音数据和采样点数
    vad = webrtcvad.Vad(int(3))#第一个参数为敏感系数，取值0-3，越大表示越敏感，越激进，对细微的声音频段都可以识别出来
    frames = frame_generator(30, audio, sample_rate)
    frames = list(frames)
    segments = vad_collector(sample_rate, 30, 300, vad, frames)
    va=0
    a=1
    for i, segment in enumerate(segments):
        path = 'chunk-%002d.wav' % (i,)
        print('--end')
        write_wave(path, segment, sample_rate)
        va+=1

    f=open("./f.txt","r")
    d=open("./output.txt","w")
    t=open("./translate.txt","w")
    for i in range(0,va):
        if(sys.argv[3]=='baidu'):#1537为中文 1737为英文
            if(sys.argv[1]=='zh'):
                result=client.asr(get_file_content('chunk-%002d'%(i,)+'.wav'), 'wav', 16000, {'dev_pid': 1537,})
            elif(sys.argv[1]=='en') :
                result=client.asr(get_file_content('chunk-%002d'%(i,)+'.wav'), 'wav', 16000, {'dev_pid': 1737,})
        elif(sys.argv[3]=='xunfei'):
                result=xunfei_recognition('chunk-%002d'%(i,)+'.wav',sys.argv[1])
    
        sound1 = AudioSegment.from_file('chunk-%002d'%(i,)+'.wav', format="wav")
        duration_in_seconds = str(len(sound1)/1000)
        start_time=get_time(0)
        end_time=get_time(len(sound1)/1000)
        print(len(sound1)/1000)
        if(sys.argv[3]=='baidu'):
            if (result['err_no'] == 0 and result['err_msg']=='success.'):	
                temp=f.readline().strip('\n')
                st=temp+'{mresult}'.format(mresult=result['result'][0])
                #tr=temp+'{mresult}'.format(mresult=translate(result['result'][0],'zh','en'))
                #t.write(tr)
                #t.write('\n')
                d.write(st)
                d.write('\n')
                d.write(baidu_translate(result['result'][0],sys.argv[1],sys.argv[2]))   
                d.write('\n')
            else:	
                st=f.readline().strip('\n')+"."
                d.write(st)
                d.write("\n")
        elif(sys.argv[3]=='xunfei'):
             temp=f.readline().strip('\n')
             st=temp+'{mresult}'.format(mresult=result)
             d.write(st)
             d.write('\n')
             d.write(baidu_translate(result,sys.argv[1],sys.argv[2]))   
             d.write('\n')
        os.remove('chunk-%002d'%(i,)+'.wav')

    f.close()
    os.remove("./f.txt")

if __name__ == '__main__':
    main(sys.argv)
