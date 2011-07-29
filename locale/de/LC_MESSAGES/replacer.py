read_from = "django.po"
write_to = "djangy.po"

f = open(read_from, 'r+')
o = open(write_to, 'w+')

for line in f:
    line = line.replace('msgstr ""','msgstr "XXXXXXXX"')
    o.write(line)

o.close()