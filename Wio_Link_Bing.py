import logging
import mraa
import time
import os
import signal
from threading import Thread, Event
from respeaker import Microphone
from respeaker.bing_speech_api import BingSpeechAPI

# get a key from https://www.microsoft.com/cognitive-services/en-us/speech-api
BING_KEY = '7c105517d6194cccb48c2b299c03dbe1'
WIO_TOKEN = 'd03eb7ea21b03d453a9c75faf45f0fce'

x = mraa.Gpio(2)
x.dir(mraa.DIR_OUT)

def get_temperature(self):
    url = 'https://cn.wio.seeed.io/v1/node/GroveTempHumD0/temperature?access_token=%s' % (WIO_TOKEN,)
    request = Request(url)
    try:
        response = urlopen(request)
        data = response.read()
        result = json.loads(data)
        if result['celsius_degree']:
            self.temperature = result['celsius_degree']
    except Exception:
        self.temperature = 0.0

def task(quit_event):
    mic = Microphone(quit_event=quit_event)
    bing = BingSpeechAPI(key=BING_KEY)

    while not quit_event.is_set():
        if mic.wakeup('respeaker'):
            print('Wake up')
            data = mic.listen()
            try:
                text = bing.recognize(data)
                if text:
                    print('Recognized %s' % text)
                    if 'temperature' in text:
                        print get_temperature()
            except Exception as e:
                print(e.message)


def main():
    logging.basicConfig(level=logging.DEBUG)
    quit_event = Event()

    def signal_handler(sig, frame):
        quit_event.set()
        print('quit')
    signal.signal(signal.SIGINT, signal_handler)

    thread = Thread(target=task, args=(quit_event,))
    thread.daemon = True
    thread.start()
    while not quit_event.is_set():
        time.sleep(1)

    time.sleep(1)


if __name__ == '__main__':
    main()
