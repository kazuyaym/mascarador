#!/usr/bin/python3
#
#
#
#
#
#############################################################################
import cgi
import cgitb; cgitb.enable()
import csv
import sys
import hashlib
import re
import binascii
import base64
from Crypto.Cipher import AES
from Crypto import Random

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

#
#
#
#############################################################################
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

#
#	Funcao que transforma todos os elementos  
#	alpha-numericos de uma string em X
#
#############################################################################
def hide(string):
	return re.sub(r'[0-9a-zA-Z]', "X", string)

#
#############################################################################
def hidel4(string):
	return string[-4:].rjust(len(string), "*")

#############################################################################
jquery = "//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"
print('Content-type:text/html\r\n\r\n')

############## Head ##############
print("""<head>
<meta content="text/html;charset=utf-8" http-equiv="Content-Type">
<meta content="utf-8" http-equiv="encoding">
<link rel="stylesheet" type="text/css" href="css/mascarador.css">
<link rel="stylesheet" type="text/css" href="css/bootstrap.css">
<link rel="stylesheet" type="text/css" href="css/bootstrap-theme.css">
<script type="text/javascript" src="js/jquery.min.js"></script>
<script type="text/javascript" src="js/edit_file.js"></script>
</head>""")

############## Body ##############
print('<body>\n')

form = cgi.FieldStorage()

a_quo = str(form.getvalue("quoting"))
if(a_quo == 'q0'): 	a_quoting = csv.QUOTE_MINIMAL
elif(a_quo == 'q1'): a_quoting = csv.QUOTE_NONNUMERIC
elif(a_quo == 'q2'): a_quoting = csv.QUOTE_NONE

a_del = str(form.getvalue("delimiter"))
if(a_del == 'd1'): a_delimiter = ','
elif(a_del == 'd2'): a_delimiter = '|'
elif(a_del == 'd3'): a_delimiter = ';'
elif(a_del == 'd4'): a_delimiter = '\t'
else: a_delimiter = str(form.getvalue("otherDelimiter"))

a_qc = str(form.getvalue("quotingchar"))
if(a_qc == 'qc1'): a_quotechar = '"'
elif(a_qc == 'qc2'): a_quotechar = "'"
else: a_quotechar = str(form.getvalue("otherQuote"))

a_s = str(form.getvalue("skipspace"))
if(a_s == 'on'): a_skip = True
else: a_skip = False

f = open(str(form.getvalue("filename")), 'r')
reader = csv.reader(f, delimiter=a_delimiter, quotechar=a_quotechar, quoting=a_quoting, skipinitialspace=a_skip)

col_count = len(next(reader))
row_count = sum(1 for row in reader) + 1
f.seek(0)

if(form.getvalue("header") == 'y'):
	row = next(reader)
	row_count -= 1
else:
	row = []
	for col in range(1, col_count+1):
		row.append("Col"+str(col))

file_name = re.search( r'\/([^/]+)$', str(form.getvalue("filename")), flags=0)

print('<form action="save_file.py" method="post">\n')
print('<h2>Information about the file:</h2>\n')
print('Input file: ~'+ str(str(form.getvalue("filename"))) +'<br>\n')
print('Output file: ~/tmp/<input type="text" name="output_filename" value="masked_' + file_name.group(1) + '"/><br>\n');
print('Number of lines: '+str(row_count)+'<br>\n')
print('Number of columns: '+ str(col_count)+'<br>\n')

print('Number of lines to write. ')
print('Choose: ')
print('Option 1:<input type="radio" name="opcao_saveLines" value="1" checked> From ')
print('<input type="number" name="lines_from" maxlength="9" max="'+str(row_count)+'" min="1" value="1" style="width: 7em"/> until')
print('<input type="number" name="lines_until" maxlength="9" max="'+str(row_count)+'" min="1" style="width: 7em" value="'+str(row_count)+'"/> / ')
print('Option 2:<input type="radio" name="opcao_saveLines" value="2"> ')
print('<input type="number" name="random_lines" style="width: 7em" maxlength="9" max="'+str(row_count)+'" min="1" value="'+str(row_count)+'"/> random lines<br>')

print('<h2>Select the columns you wish to change (mask or delet): </h2>\n')
print('<input type="text" name="filename" value="' + str(form.getvalue("filename")) + '" class="desaparece noshow"/>\n')
print('<input type="text" name="header" value="' + str(form.getvalue("header")) + '" class="desaparece noshow"/>\n')

print('<table>\n')
col = 1
print('<tr class="sucess">\n')
for element in row:
	print('<th>\n')
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
</body>
</html>""")

f.close()