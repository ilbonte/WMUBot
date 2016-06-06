import StringIO
import json
import logging
import random
import urllib
import urllib2

# for sending images
from PIL import Image
import multipart

# for checking if service avaiable
from datetime import datetime

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

TOKEN = 'INSERISCI IL TOKEN DEL BOT'

BASE_URL = 'https://api.telegram.org/bot' + TOKEN + '/'


# ================================

class EnableStatus(ndb.Model):
    # key name: str(chat_id)
    enabled = ndb.BooleanProperty(indexed=False, default=False)


# ================================

def setEnabled(chat_id, yes):
    es = EnableStatus.get_or_insert(str(chat_id))
    es.enabled = yes
    es.put()


def getEnabled(chat_id):
    es = EnableStatus.get_by_id(str(chat_id))
    if es:
        return es.enabled
    return False


# ================================

class MeHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getMe'))))


class GetUpdatesHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        self.response.write(json.dumps(json.load(urllib2.urlopen(BASE_URL + 'getUpdates'))))


class SetWebhookHandler(webapp2.RequestHandler):
    def get(self):
        urlfetch.set_default_fetch_deadline(60)
        url = self.request.get('url')
        if url:
            self.response.write(
                json.dumps(json.load(urllib2.urlopen(BASE_URL + 'setWebhook', urllib.urlencode({'url': url})))))


class WebhookHandler(webapp2.RequestHandler):


    def post(self):
        urlfetch.set_default_fetch_deadline(60)
        body = json.loads(self.request.body)
        logging.info('request body:')
        logging.info(body)
        self.response.write(json.dumps(body))

        update_id = body['update_id']
        message = body['message']
        message_id = message.get('message_id')
        date = message.get('date')
        text = message.get('text')
        fr = message.get('from')
        chat = message['chat']
        chat_id = chat['id']

        if not text:
            logging.info('no text')
            return

        def reply(msg=None, img=None):
            if msg:
                resp = urllib2.urlopen(BASE_URL + 'sendMessage', urllib.urlencode({
                    'chat_id': str(chat_id),
                    'text': msg.encode('utf-8'),
                    'disable_web_page_preview': 'true',
                    'reply_to_message_id': str(message_id),
                })).read()
            elif img:
                resp = multipart.post_multipart(BASE_URL + 'sendPhoto', [
                    ('chat_id', str(chat_id)),
                    ('reply_to_message_id', str(message_id)),
                ], [
                                                    ('photo', 'image.jpg', img),
                                                ])
            else:
                logging.error('no msg or img specified')
                resp = None

            logging.info('send response:')
            logging.info(resp)

        # povo - Mostra le Webcam delle mense di Povo
        # mesiano - Mostra le Webcam delle mense di Mesiano
        # lettere - Mostra le Webcam della mensa in via Tommaso Gar
        # help - Mostra la lista di cose che posso fare


        def isLunchTime(decimalTime):
            if decimalTime > 11.45 and decimalTime < 14.30:
                return True
            else:
                return False
        def getCamImgFromUrl(url):
            file = StringIO.StringIO(urllib.urlopen(url).read())
            img = Image.open(file)
            img.save(file, 'JPEG')
            return file.getvalue()

        #cam urls
        lettere="http://ftp.tn.ymir.eu/tgar.jpg"
        povoVeloce="http://ftp.tn.ymir.eu/Povo01.jpg"
        povoNormale="http://ftp.tn.ymir.eu/Povo02.jpg"
        mesiano1="http://ftp.tn.ymir.eu/mesiano01.jpg"
        mesiano2="http://ftp.tn.ymir.eu/mesiano02.jpg.jpg" #note: is not a typo! They are acutally using double extension :|

        notAvailableMsg = "Il servizio webcam e' attivo solo dalle 11.45 alle 14.30, sorry bro :( "
        if text.startswith('/'):
            currentHour = (datetime.utcnow().hour + 2) / 1.0
            currentMin = (datetime.utcnow().minute) / 100.0
            decimalTime = float(currentHour) + float(currentMin)
            strTime = str(decimalTime)
            if text == '/start':
                reply('Bot abilitato. Usa /stop per disabilitarimi')
                setEnabled(chat_id, True)
            elif text == '/stop':
                reply('Bot disabilitato. Usa /start per abilitarmi')
                setEnabled(chat_id, False)
            elif text == '/test':
                reply(strTime)
                reply(img=getCamImgFromUrl(lettere))
                reply(img=getCamImgFromUrl(povoVeloce))
                reply(img=getCamImgFromUrl(povoNormale))
                reply(img=getCamImgFromUrl(mesiano1))
                reply(img=getCamImgFromUrl(mesiano2))

            elif '/povo' in text:
                if isLunchTime(decimalTime):
                    reply(img=getCamImgFromUrl(povoVeloce))
                    reply(img=getCamImgFromUrl(povoNormale))
                else:
                    reply(notAvailableMsg)
            elif '/mesiano' in text:
                if isLunchTime(decimalTime):
                    reply(img=getCamImgFromUrl(mesiano1))
                    reply(img=getCamImgFromUrl(mesiano2))
                else:
                    reply(notAvailableMsg)
            elif '/lettere' in text:
                if isLunchTime(decimalTime):
                    reply(img=getCamImgFromUrl(lettere))
                else:
                    reply(notAvailableMsg)
            elif '/sito' in text:
                reply("http://www.operauni.tn.it/servizi/ristorazione/calendario")
            elif '/help' in text:
                reply(
                    "/povo - Mostra le Webcam delle mense di Povo\n/mesiano - Mostra le Webcam delle mense di Mesiano\n/lettere - Mostra le Webcam della mensa in via Tommaso Gar\n/sito - Invia il link del sito per ulteriori info (menu', calendario, ecc)\n/help - Mostra sta roba qui")
                reply("Se pensi che ci sia qualcosa di rotto contatta @ilbonte e magari manda uno screen\n")
            elif '/nanno' in text:
                file = StringIO.StringIO(
                    urllib.urlopen('https://pbs.twimg.com/profile_images/926380743/I_love_nano.jpg').read())
                img = Image.open(file)
                img.save(file, 'JPEG')
                reply(img=file.getvalue())
            #else:
                #reply("comando sconosciuto");



app = webapp2.WSGIApplication([
    ('/me', MeHandler),
    ('/updates', GetUpdatesHandler),
    ('/set_webhook', SetWebhookHandler),
    ('/webhook', WebhookHandler),
], debug=True)
