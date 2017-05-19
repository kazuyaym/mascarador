#!/usr/bin/python3
import cgi
import cgitb; cgitb.enable()
import csv
import sys
import hashlib
import re
import binascii
import base64
import os, sys
try: # Windows needs stdio set for binary mode.
	import msvcrt
	msvcrt.setmode (0, os.O_BINARY) # stdin  = 0
	msvcrt.setmode (1, os.O_BINARY) # stdout = 1
except ImportError:
	pass
import os
import errno

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
		self.iv = bytes(key[0:16], 'utf-8')

	def __pad(self, text):
		text_length = len(text)
		amount_to_pad = AES.block_size - (text_length % AES.block_size)
		if amount_to_pad == 0: amount_to_pad = AES.block_size
		pad = chr(amount_to_pad)
		return text + pad * amount_to_pad

	def __unpad(self, text):
		pad = ord(text[-1])
		return text[:-pad]

	def encrypt( self, raw ):
		raw = self.__pad(raw)
		cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
		return base64.b64encode(cipher.encrypt(raw)).decode()

	def encrypt_random(self, message):
	    IV = Random.new().read(16)
	    aes = AES.new(self.key, AES.MODE_CFB, IV)
	    return base64.b64encode(IV + aes.encrypt(message)).decode('utf-8')

def md5(string):
	if(len(string) == 0): return ""

	m = hashlib.md5()

	IV = 16 * '\x00'
	string = string + IV

	# Com essas linha abaixo: mesmos valores, terao hash diferentes
	# iv = Random.new().read(8)
	# string = string + binascii.hexlify(iv).decode("utf-8") 

	m.update(string.encode('utf-8'))
	return m.hexdigest()

def hide(string):
	return re.sub(r'[0-9a-zA-Z]', "X", string)

def hidel4(string):
	return string[-4:].rjust(len(string), "*")

##################################################################
#
#
#                                                             BODY
#
#
##################################################################
def upload_file(fn, fileitem):
	f = open('files/' + fn, 'wb', 10000)
	for chunk in fbuffer(fileitem.file): 
		f.write(chunk) # Read the file in chunks
	f.close()

def fbuffer(f, chunk_size=10000):
	while True:
		chunk = f.read(chunk_size)
		if not chunk: break
		yield chunk

def make_sure_path_exists(path):
	try:
		os.makedirs(path)
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			raise

def a_quoting(form):
	if  (str(form.getvalue("quoting")) == 'q0'): return csv.QUOTE_MINIMAL
	elif(str(form.getvalue("quoting")) == 'q1'): return csv.QUOTE_NONNUMERIC
	elif(str(form.getvalue("quoting")) == 'q2'): return csv.QUOTE_NONE

def a_delimiter(form):
	if  (str(form.getvalue("delimiter")) == 'd1'): return ','
	elif(str(form.getvalue("delimiter")) == 'd2'): return '|'
	elif(str(form.getvalue("delimiter")) == 'd3'): return ';'
	elif(str(form.getvalue("delimiter")) == 'd4'): return '\t'
	else:                                          return str(form.getvalue("otherDelimiter"))

def a_quotechar(form):
	if  (str(form.getvalue("quotingchar")) == 'qc1'): return '"'
	elif(str(form.getvalue("quotingchar")) == 'qc2'): return "'"
	else:                                             return str(form.getvalue("otherQuote"))

def a_skip(form):
	if(str(form.getvalue("skipspace")) == 'on'): return True
	else:                                        return False

def header_file(form, reader, row_count, col_count):
	if(form.getvalue("header") == 'y'):
		title = next(reader)
		row_count -= 1
	else:
		title = []
		for col in range(1, col_count+1): title.append("Col"+str(col))
	return title, row_count

def is_safeName(fileitem):
	t = re.compile("[a-zA-Z0-9.,_-]")
	for ch in fileitem.filename:
		if not t.match(ch):
			return False
	return True

def print_head():
	print("""<head>
	<meta content="text/html;charset=utf-8" http-equiv="Content-Type">
	<meta content="utf-8" http-equiv="encoding">
	<link rel="stylesheet" type="text/css" href="css/bootstrap.css">
	<link rel="stylesheet" type="text/css" href="css/bootstrap-theme.css">
	<link rel="stylesheet" type="text/css" href="css/mascarador.css">
	<script type="text/javascript" src="js/jquery.min.js"></script>
	<script type="text/javascript" src="js/edit_file.js"></script>
	</head>""")

def print_initBody(fn, row_count, col_count):
	print('<body>\n')
	print('<div class="container">\n')
	print('<form action="save_file.py" method="post">\n')
	print('<h2>Information about the file:</h2>\n')
	print('Input file: '+ fn +'<br>\n')
	print('Number of lines: '+str(row_count)+'<br>\n')
	print('Number of columns: '+ str(col_count)+'<br>\n')

def print_lines(row_count, col_count):
	print('<div id="block_container">')
	print("""Lines to write:
	<select id="opcao_saveLines" name="opcao_saveLines" onchange=lines_option()>
	<option value="lAll">All lines</option>
	<option value="lSubset">Subset</option>
	<option value="lRandom">Random</option>
	</select>""")

	print('<div id="subset_lines">')
	print('From <input type="number" id="lf" name="lines_from" maxlength="9" max="' + str(row_count) + '" min="1" value="1" style="width: 7em"/> until')
	print('<input type="number" id="lu" name="lines_until" maxlength="9" max="' + str(row_count) + '" min="1" style="width: 7em" value="' + str(row_count) + '"/>')
	print('</div>')

	print('<div id="random_lines">')
	print('<input type="number" name="random_lines" style="width: 7em" maxlength="9" max="' + str(row_count) + '" min="1" value="' + str(row_count) + '"/> random lines<br>')
	print('</div>')
	print('</div>')

def print_hideForm(fn, form):
	print('<h2>Select the columns you wish to change (mask or delet): </h2>\n')
	print('<input type="text" name="filename" value="' + fn + '" class="desaparece noshow"/>\n')
	print('<input type="text" name="header"           value="' + str(form.getvalue("header"))           + '" class="desaparece noshow"/>\n')
	print('<input type="text" name="quoting_open"     value="' + str(form.getvalue("quoting"))     + '" class="desaparece noshow"/>\n')
	print('<input type="text" name="delimiter_open"   value="' + str(form.getvalue("delimiter"))   + '" class="desaparece noshow"/>\n')
	print('<input type="text" name="quotingchar_open" value="' + str(form.getvalue("quotingchar")) + '" class="desaparece noshow"/>\n')
	print('<input type="text" name="skipspace_open"   value="' + str(form.getvalue("skipspace"))   + '" class="desaparece noshow"/>\n')
	print('<input type="text" name="otherDelimiter_open" value="' + str(form.getvalue("otherDelimiter")) + '" class="desaparece noshow"/>\n')
	print('<input type="text" name="otherQuote_open"     value="' + str(form.getvalue("otherQuote"))     + '" class="desaparece noshow"/>\n')

def print_table(reader, title, row_count):
	print('<div style="overflow:auto">\n')
	print('<table class="table table-striped table-bordered table-condensed">\n')
	col = 1
	print('<tr>\n')
	for element in title:
		print('<th style="white-space:nowrap;">\n')
		print('<input id="chek' + str(col) + '" type="checkbox" name="chek' + str(col) + '" onclick="show_modo(' + str(col) + ')">\n')
		print('<select id="sel' + str(col) + '" name="mask'+str(col)+'" class="desaparece" onchange="change_modo(' + str(col) + ')">\n')
		print('		<option value="m1">Hash MD5</option>\n')
		print('		<option value="m2">AES Encrypt</option>\n')
		print('		<option value="m5">AES Decrypt</option>\n')
		print('		<option value="m7">AES Random Encrypt</option>\n')
		print('		<option value="m8">AES Random Decrypt</option>\n')
		print('		<option value="m3">Hide Value</option>\n')
		print('		<option value="m6">Credit Card</option>\n')
		print('		<option value="m4">Delete Column</option>\n')
		print('</select>\n')
		print('<input type="text" name="name'+str(col)+'" value="'+str(element)+'">\n')
		print('</th>\n')
		col += 1
	print('</tr>\n')

	e = AESCipher('#teste0123456789')
	lin = 1
	for row in reader:
		print('<tr>\n')
		col = 1
		for element in row:
			print('<td id="l' + str(lin) + 'c' + str(col) + 'm0" >' + element + '</td>\n')
			print('<td id="l' + str(lin) + 'c' + str(col) + 'm1" class="desaparece">' + md5(element) + '1</td>\n')
			print('<td id="l' + str(lin) + 'c' + str(col) + 'm2" class="desaparece">' + e.encrypt(element) + '</td>\n')
			print('<td id="l' + str(lin) + 'c' + str(col) + 'm5" class="desaparece">Decrypt("'+element+'")</td>\n')
			print('<td id="l' + str(lin) + 'c' + str(col) + 'm7" class="desaparece">' + e.encrypt_random(element) + '</td>\n')
			print('<td id="l' + str(lin) + 'c' + str(col) + 'm8" class="desaparece">Decrypt_random("'+element+'")</td>\n')
			print('<td id="l' + str(lin) + 'c' + str(col) + 'm3" class="desaparece">' + hide(element) + '</td>\n')
			print('<td id="l' + str(lin) + 'c' + str(col) + 'm6" class="desaparece">' + hidel4(element) + '</td>\n')
			print('<td id="l' + str(lin) + 'c' + str(col) + 'm4" class="desaparece"></td>\n')
			col += 1
		print('</tr>\n')
		lin += 1
		if lin > 10: break

	print('</table>\n')
	print('</div>')
	print('<input type="hidden" value="' + str(row_count) + '" name="numeroLinhas" />\n')

	print(
	"""<p><strong>Type a password containing 16 caracter for AES Crypt or for salt usage in MD5 Hashing:</strong>
	<input type="text" id="psw1" name="psw1" value="" onkeyup="status_pwd()"><br>

	<strong>Choose the delimiter to separate fields:</strong>
	<select id="delimiter" name="delimiter">
			<option value="d1">, (Comma)     </option>
			<option value="d2">| (Pipe)      </option>
			<option value="d3">; (Semicolon) </option>
			<option value="d4">(Tab)         </option>
	</select><br>

	<strong>Quoting method:</strong>
	<select id="quoting" name="quoting">
			<option value="q0">Minimal     </option>
			<option value="q1">All         </option>
			<option value="q2">Non-numeric </option>
			<option value="q3">None        </option>
	</select>

	<select id="quotingchar" name="quotingchar">
			<option value="qc1">"value" </option>
			<option value="qc2">'value' </option>
	</select>
	<br>MINIMAL: Only quote fields which contain special characters such as delimiter or quotechar.
	<br>ALL: Quote all fields.
	<br>NON-NUMERIC: Quote all non-numeric fields.
	<br>NONE: Never quote fields.

	<p><input type="submit" name="start" value="Save file" disabled /></p>
	</form>
	</div>
	</body>
	</html>""")

##################################################################
#
#
#                                                             MAIN
#
#
##################################################################
form = cgi.FieldStorage()
fileitem = form["filename1"]
print('Content-type:text/html\r\n\r\n')

if fileitem.filename and is_safeName(fileitem):
	fn = os.path.basename(fileitem.filename)

	upload_file(fn, fileitem)

	f = open('files/' + fn, 'r')
	reader = csv.reader(f, delimiter=a_delimiter(form), quotechar=a_quotechar(form), quoting=a_quoting(form), skipinitialspace=a_skip(form))
	col_count = len(next(reader))
	row_count = sum(1 for row in reader) + 1
	f.seek(0)

	title, row_count = header_file(form, reader, row_count, col_count)
	print_head()
	print_initBody(fn, row_count, col_count)
	print_lines(row_count, col_count)
	print_hideForm(fn, form)
	print_table(reader, title, row_count)

	f.close()