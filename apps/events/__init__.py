#import csv
#
#from events.models import TypeColorSet
#
#color_reader = csv.reader(open('colors.csv', 'rb'))
#
#for row in color_reader:
#    TypeColorSet.objects.create(fg_color='FFF', bg_color=row[0], border_color=row[1])