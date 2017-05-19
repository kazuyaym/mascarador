#!/usr/bin/python3
import cgi
import cgitb; cgitb.enable()
import csv
import sys
import hashlib
import re
import binascii
import random
import time
import base64
import os
from Crypto.Cipher import AES
from Crypto import Random

##################################################################
#
#
#                                                     MASK METHODS
#
#
##################################################################
class AESCipher:
	def __init__(self, key):
		self.key = key
		self.iv  = bytes(key[0:16], 'utf-8')

	def __pad(self, text):
		text_length   = len(text)
		amount_to_pad = AES.block_size - (text_length % AES.block_size)
		if amount_to_pad == 0: amount_to_pad = AES.block_size
		pad = chr(amount_to_pad)
		return text + pad * amount_to_pad

	def __unpad(self, text):
		pad = ord(text[-1])
		return text[:-pad]

	def encrypt( self, text ):
		if(len(text) == 0): return ""
		text = self.__pad(text)
		cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
		return base64.b64encode(cipher.encrypt(text)).decode()

	def decrypt( self, inputText ):
		text = inputText
		if(len(text) == 0): return ""
		try: 
			text   = base64.b64decode(text.encode())
			cipher = AES.new(self.key, AES.MODE_CBC, self.iv )
			de     = self.__unpad(cipher.decrypt(text).decode("utf-8"))
		except: 
			time.sleep(1)
			de = inputText
		return de

	def encrypt_random(self, text):
		if(len(text) == 0): return ""
		IV = Random.new().read(16)
		aes = AES.new(self.key, AES.MODE_CFB, IV)
		return base64.b64encode(IV + aes.encrypt(text)).decode('utf-8')

	def decrypt_random(self, inputText):
		text = inputText
		if(len(text) == 0): return ""
		try: 	
			text = base64.b64decode(text.encode('utf-8'))
			IV   = text[:16]
			aes  = AES.new(self.key, AES.MODE_CFB, IV)
			de   = aes.decrypt(text[16:]).decode('utf-8')
		except: 
			time.sleep(1)
			de = inputText
		return de

def md5(key, text):
	if(len(text) == 0): return ""
	m = hashlib.md5()
	text = text + key
	m.update(text.encode('utf-8'))
	return m.hexdigest()

def md5_randomSalt(text):
	if(len(text) == 0): return ""
	iv = Random.new().read(8)
	text = text + binascii.hexlify(iv).decode("utf-8") 
	m.update(text.encode('utf-8'))
	return m.hexdigest()

def hide(text):
	return re.sub(r'[0-9a-zA-Z]', "X", text)

def hidel4(text):
	return text[-4:].rjust(len(text), "*")

##################################################################
#
#
#                                                             BODY
#
#
##################################################################
def a_delimiter_open(form):
	if  (str(form.getvalue("delimiter_open")) == 'd1'): return ','
	elif(str(form.getvalue("delimiter_open")) == 'd2'): return '|'
	elif(str(form.getvalue("delimiter_open")) == 'd3'): return ';'
	elif(str(form.getvalue("delimiter_open")) == 'd4'): return '\t'
	else: return str(form.getvalue("otherDelimiter_open"))

def a_quotechar_open(form):
	if  (str(form.getvalue("quotingchar_open")) == 'qc1'): return '"'
	elif(str(form.getvalue("quotingchar_open")) == 'qc2'): return "'"
	else: return str(form.getvalue("otherQuote_open"))

def a_quoting_open(form):
	if  (str(form.getvalue("quoting_open")) == 'q0'): return csv.QUOTE_MINIMAL
	elif(str(form.getvalue("quoting_open")) == 'q1'): return csv.QUOTE_NONNUMERIC
	elif(str(form.getvalue("quoting_open")) == 'q2'): return csv.QUOTE_NONE

def a_skip_open(form):
	if(str(form.getvalue("skipspace_open")) == 'on'): return True
	else: return False

def a_quoting(form):
	if  (str(form.getvalue("quoting")) == 'q0'): return csv.QUOTE_MINIMAL
	elif(str(form.getvalue("quoting")) == 'q1'): return csv.QUOTE_ALL
	elif(str(form.getvalue("quoting")) == 'q2'): return csv.QUOTE_NONE
	else: return csv.QUOTE_NONE

def a_delimiter(form):
	if  (str(form.getvalue("delimiter")) == 'd1'): return ','
	elif(str(form.getvalue("delimiter")) == 'd2'): return '|'
	elif(str(form.getvalue("delimiter")) == 'd3'): return ';'
	else: return '\t'

def a_quotechar(form):
	if(str(form.getvalue("quotingchar")) == 'qc1'): return '"'
	else: return "'"

form = cgi.FieldStorage()
print('Content-type:text/html\r\n\r\n')

filename        = str(form.getvalue("filename"))
header          = str(form.getvalue("header"))
opcao_saveLines = str(form.getvalue("opcao_saveLines"))
lines_from      = int(form.getvalue("lines_from"))
lines_until     = int(form.getvalue("lines_until"))
random_lines    = int(form.getvalue("random_lines"))

f = open("files/" + filename, 'r')
reader = csv.reader(f, delimiter=a_delimiter_open(form), quotechar=a_quotechar_open(form), quoting=a_quoting_open(form), skipinitialspace=a_skip_open(form))
col_count = len(next(reader))
row_count = sum(1 for row in reader) + 1
f.seek(0)

if(form.getvalue("header") == 'y'):	
	title = next(reader)
	row_count -= 1

outfile = "files/masked_" + filename
fout = open(outfile, 'w', newline='')
writer = csv.writer(fout, delimiter=a_delimiter(form), quotechar=a_quotechar(form), quoting=a_quoting(form))

# Quais linhas serao salvas
if(opcao_saveLines == 'lRandom'):
	lines = random.sample(range(1, row_count+1), random_lines)
	lines.sort()
else: lines = list(range(lines_from, lines_until+1))

# O que fazer com cada coluna?
colMaskOn = []
title = []
for i in range(1, col_count+1):
	t = "name" + str(i)
	title.append(str(form.getvalue(t)))
	
	if(str(form.getvalue("chek"+str(i))) == "on"):
		m = "mask"+str(i)
		if(  str(form.getvalue(m)) == "m1"): colMaskOn.append(1)
		elif(str(form.getvalue(m)) == "m2"): colMaskOn.append(2)
		elif(str(form.getvalue(m)) == "m3"): colMaskOn.append(3)
		elif(str(form.getvalue(m)) == "m5"): colMaskOn.append(5)
		elif(str(form.getvalue(m)) == "m6"): colMaskOn.append(6)
		elif(str(form.getvalue(m)) == "m7"): colMaskOn.append(7)
		elif(str(form.getvalue(m)) == "m8"): colMaskOn.append(8)		
		else: 
			colMaskOn.append(-1)
			title.pop(len(title)-1)
	else: colMaskOn.append(0)

writer.writerow(title)

key = str(form.getvalue("psw1"))
cipher = AESCipher(key)

print("""<head>
<meta content="text/html;charset=utf-8" http-equiv="Content-Type">
<meta content="utf-8" http-equiv="encoding">
<link rel="stylesheet" type="text/css" href="css/mascarador.css">
</head>

<body>
<h1>Arquivo salvo com sucesso!</h1>

<form action="download_file.py">""")

k = 0
for row in reader:
	k += 1
	if(not lines): break
	if(lines[0] != k): continue
	if not row: continue

	lines.pop(0)
	for i in range(col_count-1,-1, -1):
		command = colMaskOn[i]
		if( command == -1): del row[i]
		elif(command == 1): row[i] = md5(key, row[i])
		elif(command == 2): row[i] = cipher.encrypt(row[i])
		elif(command == 3): row[i] = hide(row[i])
		elif(command == 5): row[i] = cipher.decrypt(row[i])
		elif(command == 6): row[i] = hidel4(row[i])
		elif(command == 7): row[i] = cipher.encrypt_random(row[i])
		elif(command == 8): row[i] = cipher.decrypt_random(row[i])
	writer.writerow(row)

f.close()
fout.close()
os.remove("files/" + filename)

print('<input type="text" name="filename" value="masked_' + filename + '" class="desaparece noshow"/>\n')
print("""<input type="submit" value="Download"/>
</form>
</body>
</html>""")