# -*- coding: utf-8 -*-

import kkm
import sys,os
import re
import json
from decimal import Decimal
from kkm import *
import kkm.Exceptions
from datetime import datetime, date, time
from struct import *
#import kkm.Atol
#import kkm.transCoding
#from kkm import *

class myKKM:
  def __init__(self):
      try:
        self.port = os.environ.get('KKMPORT','ttyACM0')
        self.baudrate = os.environ.get('KKMBAUDRATE',115200)
        self.kkm = kkm.KkmMeta.autoCreate({'port': '/dev/'+self.port, 'baudrate': self.baudrate})
      except Exception, msg:
        self.ShowError(msg)
        self.ShowError(msg or 'Не найден кассовый аппарат или не определён серийный номер.')
        raise
      finally:
        print "Connected to %s with serial: %s at port/speed: /dev/%s:%s"%(self.kkm.typeDev['name'],str(self.kkm.getKKMId()).zfill(8),self.port,self.baudrate)
        self.mode=self.kkm.GetCurrentMode()
        
#      self.RegisterDevice()

  def CheckZReport(self):
      if self.kkm.isCheckOpen():
          self.kkm.Annulate()
      try:
            self.kkm.ResetMode()
            self.kkm.setRegistrationMode(1)
      except kkm.Exceptions.KKMNeedZReportErr:
            print "Start ZReportMode"
            self.kkm.setZReportMode(30)
            self.kkm.Report(kkm_Z_report)
            self.CheckZReport()
      except kkm.Exceptions.KKMException, msg:
            self.ShowError(msg)

#  def RegisterDevice(self):
#      global kkmDev
#      kkmDev = self.kkm

  def tmps12314(self):
    try:
            self.kkm.setRegistrationMode(1)
            if self.kkm.isCheckOpen():
                self.kkm.Annulate()
    except kkm.Exceptions.KKMNeedZReportErr:
            print "Start ZReportMode"
            self.kkm.setZReportMode(30)
            self.kkm.Report(kkm_Z_report)
            self.RegisterDevice()
    except kkm.Exceptions.KKMException, msg:
            self.ShowError(msg)
#        try:
#            kkmDev.ResetMode()
#        except kkm.Exception.KKMException, msg:
#            self.ShowError(msg)
    else:
            if self.kkm.isCheckOpen():
                self.kkm.Annulate()
                                        
  def ShowError(self,msg):
      print(msg)
  
  def PrintBron(self,content):
      self.kkm.ByPassKKM('\x1b\xfa\x01\x00\x64\x00\xf0') # печать картинки
      self.kkm.PrintCustom("\tБ\tР\tО\tН\tИ\tР\tО\tВ\tА\tН\tИ\tЕ",center=1,magnify=1,fmt=5)
      bronnum = "\t".join(str(content['number'].encode('utf-8')))
      self.kkm.PrintCustom("Номер бронирования: \t%s"%bronnum,center=1,magnify=1,fmt=1)
      self.kkm.PrintString("")
      self.kkm.PrintCustom("Время бронирования: %s"%content['bronopen'].encode('utf-8'),center=1,magnify=3,fmt=0)
      self.kkm.PrintCustom("Бронь действительна до:",center=1)
      self.kkm.PrintCustom("%s"%content['bronuntil'].encode('utf-8'),center=1)
      self.kkm.PrintString("")
      self.kkm.PrintCustom(content['title'].encode('utf-8'),magnify=1,center=1)
      self.kkm.PrintString("")
      self.kkm.PrintCustom("Стоимость: %s руб."%content['price'].encode('utf-8'),center=1,magnify=1,fmt=1)
      self.kkm.PrintString("")
      self.kkm.BarCodePrint(content['barcode'].encode('utf-8'))
      self.kkm.PrintCustom("   ",center=1,magnify=0,fmt=0)
      self.kkm.PrintCustom("Билеты действителены только после оплаты",center=1,magnify=3,fmt=0)
      self.kkm.PrintCustom("на кассе",center=1)
      self.kkm.CutCheck()
  
  def PrintCheck(self):
#      self.CheckZReport()
      try:
          if self.kkm.isCheckOpen():
              self.kkm.Annulate()
          self.kkm.OpenCheck()#checkType=kkm.kkm_Annulate_check)
          summ = 0
          for pos in self.check:
              discount = 0
              discount = int(pos['discount'].strip())
              if discount == 0:
	          self.kkm.Sell(pos['title'].encode('utf-8').strip(), float(pos['price'].strip()), float(1), 0)
                  summ += float(pos['price'].strip())
              else:
                  self.kkm.Sell(pos['title'].encode('utf-8').strip(), float(pos['price'].strip()), float(1), 0)
                  summ += float(pos['price'].strip())
                  self.kkm.Discount(float(discount), area=kkm.kkm_Sell_dis, type_=kkm.kkm_Sum_dis, sign_=kkm.kkm_Discount_dis)
                  summ -= float(discount)
          self.kkm.Payment(float(summ))
      except kkm.Exceptions.KKMException, msg:
          self.ShowError(msg)
      self.check = []

  def SettingsTable(self):
    """ Print Settings table """
    self.kkm.setProgrammingMode(30)
    print self.kkm.kkmModelParams[self.kkm.model]['tblsz']
    for i in range(self.kkm.kkmModelParams[self.kkm.model]['tblsz']+1):
#    for i in xrange(72):
      try:
        cursor = '2.1.'+str(i)
        if cursor in self.kkm.kkmModelParams[self.kkm.model]:
          (tbl,row,field) = cursor.split('.')
          res = self.kkm.AltReadTable(tbl,row,field)
          if 'type' not in self.kkm.kkmModelParams[self.kkm.model][cursor]:
            if 'values' in self.kkm.kkmModelParams[self.kkm.model][cursor]:
              if self.kkm.atol2number(res) in self.kkm.kkmModelParams[self.kkm.model][cursor]['values']:
                print self.kkm.kkmModelParams[self.kkm.model][cursor]['name'],':',self.kkm.kkmModelParams[self.kkm.model][cursor]['values'][self.kkm.atol2number(res)]
            else:
                print self.kkm.kkmModelParams[self.kkm.model][cursor]['name'],':',self.kkm.atol2number(res)
#          line = "".join([ "%s"%kkm.kkmtocp866[ord(char)].decode('cp866') for char in res ])
#          print i,"%x"%i,repr(res),line# self.kkm.atol2number(res),line
#        res = self.kkm.readTable(3,1,"%x"%i)
#        res = self.kkm.AltReadTable(3,i,1)
#        line = "".join([ "%s"%kkm.kkmtocp866[ord(char)].decode('cp866') for char in res ])
#        print i,"%x"%i,repr(res),line
        
#        res = self.kkm.AltReadTable(3,i,2)
#        line = "".join([ "%s"%kkm.kkmtocp866[ord(char)].decode('cp866') for char in res ])
#        print i,"%x"%i,repr(res),line# self.kkm.atol2number(res),line
        #repr(self.kkm.atol2number(res)),repr(res)
      except:
        pass
#    print self.kkm.getKlisheLen()
#    print self.kkm.getKlisheMax()


  def KlisheProgramming(self):
    self.klishe=[" ","\tБ\tУ\tД\tЕ\tМ \tР\tА\tД\tЫ \tВ\tИ\tД\tЕ\tТ\tЬ","\tВ\tА\tС \tС\tН\tО\tВ\tА","\"\tП\tЛ\tА\tН\tЕ\tТ\tА\tР\tИ\tЙ\"","------------------------------------------"," "]
    self.kkm.setProgrammingMode(30)
    self.kkm.writeTable(2,1,24,chr(3)) # lines after check
    self.kkm.writeTable(2,1,44,chr(7)) # lines before check
    self.kkm.setKlishe(kkmD.klishe)

    for i in self.klishe:
        encoded = i.decode('utf-8').encode('cp866')
        #    for char in encoded:
        #    print "char",repr(char),char,char.decode('cp866'),repr("%s"%kkm.cp866tokkm[ord(char)])
        #    print "repr",repr("%s"%kkm.cp866tokkm[ord(char)])
        #    print repr(unicode(char))
        line = "".join([ "%s"%kkm.cp866tokkm[ord(char)] for char in encoded ])
        print repr(line)
    print 'Existing Klishe'

    for i in xrange(0,len(self.klishe)):
        res = self.kkm.readTable(6,i,0)
        line = []
        line = "".join([ "%s"%kkm.kkmtocp866[ord(char)].decode('cp866') for char in res ])
        print i,line


  def prodazha(self,parsed_json):
#    AnnulateAndSetRegistrationMode()
    for string in parsed_json[0:4]:
        if string['type'] == 'bron':
            #pass
            kkmD.PrintBron(string)
        else:
            print("Unknown Type: %s"%string['type'])
        if string['check'] == '1':
            self.check.append(string)
    self.PrintCheck()

  def AnnulateAndSetRegistrationMode(self,_pass=1):
    if self.kkm.isCheckOpen():
        self.kkm.Annulate()
    self.kkm.ResetMode()
    print 'Pass: %s'%_pass
    self.kkm.setRegistrationMode(_pass)

  def vozvrat(self,_name,_summ,_count):
    self.kkm.ResetMode()
    self.kkm.setRegistrationMode(1)
    print 'Password: ',self.kkm._kkmPassword
    self.kkm.OpenCheck(checkType=kkm.kkm_Return_check)
    #    _checkTypeDict = {
    #        kkm.kkm_Sell_check     : 1,
    #        kkm.kkm_Return_check   : 2,
    #        kkm.kkm_Annulate_check : 3
    #        }
    self.kkm.BuyReturn(_name,_summ,_count)
#    self.kkm.AnnulateSumm(200,1)
    self.kkm.Payment(0)
    
  def FastXReport(self):
    pass

  def FastZReport(self):
    if self.kkm.isCheckOpen():
        self.kkm.Annulate()
    self.kkm.ResetMode()
    self.kkm.setZReportMode(29)
    self.kkm.Report(kkm_Z_report)

def toBinary(n):
    return ''.join(str(1 & int(n) >> i) for i in range(8)[::-1])
    
def expandbinary(value,binarray):
    expanded = []
    for i in range(8):
        bit = value & 0x1
        if binarray[i][value & 0x1] != '':
            expanded.append(binarray[i][value & 0x1])
        value = value >> 1
    return expanded

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
        '\xcc\xb1' : '',          # modifier - under line
        '\xe2\x80\x93' : '-',
        '\x20\x13' : '-'
}    

kkmD=myKKM()
#ch.setLevel(logging.INFO)
kkmD.CheckZReport()
kkmD.check = []
#self.kkm.setXReportMode(29)
#self.kkm.Report(kkm_X_report)
#kkmD.SettingsTable()
kkmD.KlisheProgramming()
#AnnulateAndSetRegistrationMode(_pass=1)

jsonstruct = '[{ "type": "bron", "number": "66666", "title": "Бронь посещения", "barcode": "123456ABCDEF", "bronopen": "7 июня 2015 19:25", "bronuntil": "7 июня 2015 19:55", "price": "1000", "check": "0" }]'

try:
    parsed_json = json.loads(jsonstruct)
except:
    print "Error Parsing json"
    raise

#self.kkm.OpenCheck()
#checkType=kkm.kkm_Annulate_check)

(cashier, site, odate, otime, flags, \
                mashine, model, version, mode, submode, \
                check, smena, checkState, checkSum, dot, port) = kkmD.kkm.GetStatus()

#val = ''
#i = 0
#print repr(bytearray(self.kkm.bcd2int('\x11\x10\x30')))
#bdate = self.kkm.bcd2int(bdate)
#btime = self.kkm.bcd2int(btime)
#bdate[0] = bdate[0]+2000
report = """
    Кассир:\t%d
    Номер в зале:\t%d
    Дата/время:\t%s
    Флаги:\t%s
    Зав.номер:\t%s
    Модель:\t%s
    Версия:\t%s
    Режим:\t%s.%s
    Номер чека:\t%s
    Номер смены:%s
    %s %s %s %s
"""

kkmstatusflags = {
        0: ['ККТ не фискализирована','ККТ фискализирована'],
        1: ['Смена закрыта','Смена открыта'],
        2: ['Денежный ящик открыт','Денежный ящик закрыт'],
        3: ['',''],
        4: ['',''],
        5: ['Крышка закрыта','Крышка открыта'],
        6: ['',''],
        7: ['Батарея ОК','Батарея разряжена']
        }

expandedflags='\n\t\t'.join(expandbinary(flags,kkmstatusflags))

kkmD.AnnulateAndSetRegistrationMode(_pass=1)
kkmD.prodazha(parsed_json)
#kkmD.AnnulateAndSetRegistrationMode(_pass=2)
#kkmD.prodazha(parsed_json)
#kkmD.AnnulateAndSetRegistrationMode(_pass=3)
#kkmD.prodazha(parsed_json)
#kkmD.AnnulateAndSetRegistrationMode(_pass=4)
#kkmD.prodazha(parsed_json)
#kkmD.vozvrat('Обсерватория',100,1)
#kkmD.FastZReport()

print report%(cashier,site,datetime.combine(odate,otime),expandedflags,mashine,\
                kkmD.kkm.modelTable[kkmD.kkm.model][0].encode('utf-8'),version,mode,\
                submode,check,smena,checkState, checkSum, dot, port)
print kkmD.kkm.typeDev
print kkmD.kkm.GetStatus()

#print kkmD.kkm.model
#print kkmD.kkm.kkmModelParams[kkmD.kkm.model]['name']
#print kkmD.kkm.kkmModelParams[kkmD.kkm.model]['tblsz']
#kkmD.SettingsTable()
#AnnulateAndSetRegistrationMode(_pass=1)

#if self.kkm.isCheckOpen():
#    self.kkm.Annulate()

#self.kkm.setZReportMode(29)
#self.kkm.Report(kkm_Z_report)

#sys.exit()
