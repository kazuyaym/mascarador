#!/usr/bin/python3

#############################################################################
import cgi, os
import cgitb; cgitb.enable()
form = cgi.FieldStorage()

filename = str(form.getvalue("filename"))

print("Content-Type: text/plain; charset=UTF-8")
print("Content-Disposition: attachment; filename=" + filename)
print()

fo = open("files/" + filename, "r")
while True:
	str = fo.read(10000);
	if not str: break
	print(str)
fo.close()

os.remove("files/" + filename)