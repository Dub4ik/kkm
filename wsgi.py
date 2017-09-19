# -*- coding: utf-8 -*-

import kkm
import sys
import ast
import json
from decimal import Decimal
from kkm import *
import kkm.Exceptions
from threading import Thread
from cgi import parse_qs, escape, test
import sys,pprint,locale,re
import logging

FORMAT='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('kkm')
logger.setLevel(logging.INFO)

class myKKM:
  def __init__(self):
      try:
        self.port = os.environ.get('KKMPORT','ttyAMA0')
        self.baudrate = os.environ.get('KKMBAUDRATE',115200)
        self.kkm = kkm.KkmMeta.autoCreate({'port': '/dev/'+self.port, 'baudrate': self.baudrate})
        self.kkmSerialNumber = self.kkm.getKKMId()
        self.KKM_PASSWORD=1
        self.mode=self.kkm.GetCurrentMode()
      except Exception, msg:
        self.ShowError(msg or 'Не найден кассовый аппарат или не определён серийный номер.')
        raise
      self.RegisterDevice()

  def CheckZReport(self):
      if kkmDev.isCheckOpen():
          kkmDev.Annulate()
      try:
            kkmDev.ResetMode()
            kkmDev.setRegistrationMode(1)
      except kkm.Exceptions.KKMNeedZReportErr:
            print "Start ZReportMode"
            kkmDev.setZReportMode(30)
            kkmDev.Report(kkm_Z_report)
            self.CheckZReport()
      except kkm.Exceptions.KKMException, msg:
            self.ShowError(msg)

  def RegisterDevice(self):
      global kkmDev
      kkmDev = self.kkm

  def tmps12314(self):
    try:
            kkmDev.setRegistrationMode(1)
            if kkmDev.isCheckOpen():
                kkmDev.Annulate()
    except kkm.Exceptions.KKMNeedZReportErr:
            print "Start ZReportMode"
            kkmDev.setZReportMode(30)
            kkmDev.Report(kkm_Z_report)
            self.RegisterDevice()
    except kkm.Exceptions.KKMException, msg:
            self.ShowError(msg)
#        try:
#            kkmDev.ResetMode()
#        except kkm.Exception.KKMException, msg:
#            self.ShowError(msg)
    else:
            if kkmDev.isCheckOpen():
                kkmDev.Annulate()
                                        
  def ShowError(self,msg):
      message = "%s"%msg
      self.errormessage = message.encode('utf-8')

  def PrintBron(self,content):
    try:
      kkmDev.ByPassKKM('\x1b\xfa\x01\x00\x64\x00\xf0') # печать картинки
      kkmDev.PrintCustom("\tБ\tР\tО\tН\tИ\tР\tО\tВ\tА\tН\tИ\tЕ",center=1,magnify=3,fmt=5)
      bronnum = "\t".join(str(content['number'].encode('utf-8')))
      kkmDev.PrintCustom("Номер бронирования: \t%s"%bronnum,center=1,magnify=3,fmt=1)
#      kkmDev.PrintString("")
      kkmDev.PrintCustom("Время бронирования: %s"%content['bronopen'].encode('utf-8'),center=1,magnify=3,fmt=0)
      kkmDev.PrintCustom("Бронь действительна до:",center=1)
      kkmDev.PrintCustom("%s"%content['bronuntil'].encode('utf-8'),center=1)
#      kkmDev.PrintString("")
      kkmDev.PrintCustom(content['title'].encode('utf-8'),magnify=1,center=1)
#      kkmDev.PrintString("")
      kkmDev.PrintCustom("Стоимость: %s руб."%content['price'].encode('utf-8'),center=1,magnify=3,fmt=1)
      kkmDev.PrintString("")
      kkmDev.BarCodePrint(content['barcode'].encode('utf-8'))
#      kkmDev.PrintCustom("   ",center=1,magnify=0,fmt=0)
      kkmDev.PrintCustom("Билеты действителены только после оплаты",center=1,magnify=3,fmt=0)
      kkmDev.PrintCustom("на кассе",center=1)
      kkmDev.CutCheck()
    except kkm.Exceptions.KKMException, msg:
      self.ShowError(msg)

  
  def PrintCheck(self,amount):
      self.CheckZReport()
      try:
          if kkmDev.isCheckOpen():
              kkmDev.Annulate()
          kkmDev.OpenCheck()#checkType=kkm.kkm_Annulate_check)
          summ = 0
          for pos in self.check:
              discount = 0
              discount = int(pos['discount'].strip())
              if discount == 0:
	          kkmDev.Sell(pos['title'].encode('utf-8').strip(), float(pos['price'].strip()), float(1), 0)
                  summ += float(pos['price'].strip())
              else:
                  kkmDev.Sell(pos['title'].encode('utf-8').strip(), float(pos['price'].strip()), float(1), 0)
                  summ += float(pos['price'].strip())
                  kkmDev.Discount(float(discount), area=kkm.kkm_Sell_dis, type_=kkm.kkm_Sum_dis, sign_=kkm.kkm_Discount_dis)
                  summ -= float(discount)
          if summ == amount:
             kkmDev.Payment(float(summ))
          else:
             kkmDev.Payment(float(amount))
      except kkm.Exceptions.KKMException, msg:
          self.ShowError(msg)
      self.check = []
      self.amount = 0

  def SettingsTable(self):
    """ Print Settings table """
    kkmDev.setProgrammingMode(30)
    for i in xrange(72):
      try:
#        res = kkmDev.readTable(3,1,"%x"%i)
#        res = kkmDev.AltReadTable(3,i,1)
#        line = "".join([ "%s"%kkm.kkmtocp866[ord(char)].decode('cp866') for char in res ])
#        print i,"%x"%i,repr(res),line
        res = kkmDev.AltReadTable(3,i,2)
        line = "".join([ "%s"%kkm.kkmtocp866[ord(char)].decode('cp866') for char in res ])
        print i,"%x"%i,repr(res),line# kkmDev.atol2number(res),line
        #repr(kkmDev.atol2number(res)),repr(res)
      except:
        pass
    print kkmDev.getKlisheLen()
    print kkmDev.getKlisheMax()


  def KlisheProgramming(self):
    kkmD.klishe=[" ","\tБ\tУ\tД\tЕ\tМ \tР\tА\tД\tЫ \tВ\tИ\tД\tЕ\tТ\tЬ","\tВ\tА\tС \tС\tН\tО\tВ\tА","\"\tП\tЛ\tА\tН\tЕ\tТ\tА\tР\tИ\tЙ\"","------------------------------------------"," "]
    kkmDev.setProgrammingMode(30)
    kkmDev.writeTable(2,1,24,chr(3)) # lines after check
    kkmDev.writeTable(2,1,44,chr(7)) # lines before check
    kkmDev.setKlishe(kkmD.klishe)

    for i in kkmD.klishe:
        encoded = i.decode('utf-8').encode('cp866')
        #    for char in encoded:
        #    print "char",repr(char),char,char.decode('cp866'),repr("%s"%kkm.cp866tokkm[ord(char)])
        #    print "repr",repr("%s"%kkm.cp866tokkm[ord(char)])
        #    print repr(unicode(char))
        line = "".join([ "%s"%kkm.cp866tokkm[ord(char)] for char in encoded ])
        print repr(line)
    for i in xrange(1,len(kkmD.klishe)):
        res = kkmDev.readTable(6,i,1)
        line = []
        line = "".join([ "%s"%kkm.kkmtocp866[ord(char)].decode('cp866') for char in res ])
        print i,line

def buildanswer(str,returncode):
    return str.replace('%RET%',returncode)
        

def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/html, charset=utf-8'), ('Access-Control-Allow-Origin', '*')])
#    start_response('200 OK', [('Content-Type','application/json; charset=utf-8'), ('Access-Control-Allow-Origin', '*')])
    str = """
<HTML>
<HEAD>
	<meta http-equiv="Content-Type" content="text/html; charset=UTF-8;">
</HEAD>
<BODY>
<H2>%RET%</H2>
<FORM METHOD=POST ACTION="http://10.10.10.10:3031/">
<TEXTAREA NAME="test"></TEXTAREA>
<INPUT TYPE="SUBMIT">
</FORM>
<a href="/?ZReport=yes">Print ZReport</a><BR>
<a href="/?XReport=yes">Print XReport</a><BR>
<a href="/?CashLastSession=yes">Print CashLastSession</a><BR>
<a href="/?CashInKKM=yes">Print CashInKKM</a><BR>
<a href="/?GetKKMStatus=yes">Print GetKKMStatus</a><BR>
</BODY>
</HTML>
    """

    if env['REQUEST_METHOD'] == 'GET':
        query = parse_qs(env['QUERY_STRING'])
    else:
        try:
            request_body_size = int(env.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0
        request_body = env['wsgi.input'].read(request_body_size)
        query = parse_qs(request_body)

    kkmD.errormessage = ''
    if 'ZReport' in query:
       print "Start ZReportMode"
       kkmDev.setZReportMode(29)
       kkmDev.Report(kkm_Z_report)
       kkmD.CheckZReport()
       return(buildanswer(str,'ZReport Printed'))
    elif 'XReport' in query:
       kkmDev.setXReportMode(30)
       kkmDev.Report(kkm_X_report)
       return(buildanswer(str,'XReport Printed'))
    elif 'CashOutCome' in query:
       kkmDev.setRegistrationMode(29)
       kkmDev.CashOutcome(query['CashOutCome'][0])
       print "CashOut %s"%query['CashOutCome'][0]
       return(buildanswer(str,"CashOutCome %s"%query['CashOutCome'][0]))
    elif 'CashInKKM' in query:
       return(buildanswer(str,"Money in KKM %d"%kkmDev.GetCashSummary()))
    elif 'CashLastSession' in query:
       return(buildanswer(str,"Last Session Money %d"%kkmDev.GetLastSummary()))
    elif 'GetKKMStatus' in query:
       (cashier, site, date1, time1, flags, \
       mashine, model, version, mode, submode, \
       check, smena, checkState, checkSum, dot, port) = kkmDev.GetStatus()
       #print type(kkmDev.atol2number(date))
#       print date1, time1
       return(buildanswer(str,"Device Status %s:%s"%(date1,time1)))
       #repr(kkmDev.GetStatus()))
    else:
       ticketarray = {}
    
       kkmD.amount = 0
       kkm.logger.info('Input Query: %s'%query)
       if 'test' in query:
         query = ast.literal_eval(query['test'][0])
       for keys,values in query.items():
        if 'amount' in keys:
#            print "Amount %s"%query['amount'][0]
            kkmD.amount = query['amount'][0].strip()
            kkm.logger.info('Amount: %s'%kkmD.amount)
        else:
          try:
            name,num,type = keys.replace(']','').split('[')
            if name == 'tickets':
               if num not in ticketarray:
                   ticketarray[num] = { "type":"","number":"","title":"","description":"","price":"","discount":"","date":"","row":"","seat":"","barcode":"","check":"0","bronopen":"","bronuntil":""}
               transcode = re.sub('(' + '|'.join(chars.keys()) + ')', replace_chars, values[0])
               decoded = transcode.decode('utf-8')
               ticketarray[num][type]=decoded
          except:
               pass

       kkmD.check = []
       if len(ticketarray) > 0:
         for record in ticketarray:
           string = ticketarray[record]
           if string['type'] == 'bron':
              #pass
              kkmD.PrintBron(string)
           else:
              print("Unknown Type: %s"%string['type'])
           if string['check'] == '1':
              kkmD.check.append(string)
         if len(kkmD.check) > 0:
            kkmD.PrintCheck(kkmD.amount)
       else:
           kkmD.errormessage = 'Список билетов пуст'

    if kkmD.errormessage != '':
       if kkmDev.isCheckOpen():
          kkmDev.Annulate()
       return(buildanswer(str,'{"err":"%s"}'%kkmD.errormessage))
    else:
       return(buildanswer(str,'{"err":"ok"}'))
#    return (decodedtestq)
    
# .encode('utf8')]

def replace_chars(match):
    char = match.group(0)
    return chars[char]
    
chars = {
        '\xc2\x82' : ',',        # High code comma
        '\xc2\x84' : ',,',       # High code double comma
        '\xc2\x85' : '...',      # Tripple dot
        '\xc2\x88' : '^',        # High carat
        '\xc2\x91' : '\x27',     # Forward single quote
        '\xc2\x92' : '\x27',     # Reverse single quote
        '\xc2\x93' : '\x22',     # Forward double quote
        '\xc2\x94' : '\x22',     # Reverse double quote
        '\xc2\x95' : ' ',
        '\xc2\x96' : '-',        # High hyphen
        '\xc2\x97' : '--',       # Double hyphen
        '\xc2\x99' : ' ',
        '\xc2\xa0' : ' ',
        '\xc2\xa6' : '|',        # Split vertical bar
        '\xc2\xab' : '<<',       # Double less than
        '\xc2\xbb' : '>>',       # Double greater than
        '\xc2\xbc' : '1/4',      # one quarter
        '\xc2\xbd' : '1/2',      # one half
        '\xc2\xbe' : '3/4',      # three quarters
        '\xca\xbf' : '\x27',     # c-single quote
        '\xcc\xa8' : '',         # modifier - under curve
        '\xcc\xb1' : '',         # modifier - under line
        '\xe2\x80\x93' : '-',    # Long Dash
        '\x20\x13' : '-'
}

    
kkmD=myKKM()
#ch.setLevel(logging.DEBUG)
#kkmD.CheckZReport()
kkmD.check = []
#kkmD.SettingsTable()

jsonstruct = '[{ "type": "bron", "number": "55555", "title": "Посещение музея", "barcode": "123456ABCDEF", "bronopen": "7 июня 2015 19:25", "bronuntil": "7 июня 2015 19:55", "price": "200", "check": "1" }, \
               { "type": "bron", "number": "66666", "title": "Посещение планетария", "barcode": "123456ABCDEF", "bronopen": "7 июня 2015 19:25", "bronuntil": "7 июня 2015 19:55", "price": "1000", "check": "0" }]'

