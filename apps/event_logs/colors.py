# colors from schipul_codebase_dev\cb\eventlogs\cb_eventlogs_hex.asp
# colors = { 'event_id':'hex color' }

# **************************************************
# WHEN you ADD colors here make sure and ADD them
# to the fixture as well
# ************************************************** 
colors = {
    # profiles - BLUE base - complement is ORANGE
    '120000':'3300FF', # base
    '121000':'3300FF', # add
    '122000':'3333FF', # edit
    '123000':'3366FF', # delete
    '124000':'3366FF', # search 
    '125000':'3399FF', # view

    # login
    '125200':'66CCFF',
 
     # contacts - TEAL/LIME-GREEN base
    '125114':'33CCCC', # add - contact form submitted / new user added
    '125115':'0066CC', # add - contact form submitted / user already exists
           
    # groups - BLUE GREEN base - complement is ????
    '160000':'339999', # base
    '161000':'339999', # add
    '162000':'339999', # edit
    '163000':'339999', # delete
    '164000':'339999', # search 
    '165000':'339999', # view    

    # group relationship
    '220000':'00CCFF', # base
    '221000':'00CCFF', # add
    '222000':'00CCFF', # edit
    '223000':'00CCFF', # delete
    '224000':'00CCFF', # search 
    '225000':'00CCFF', # view   
 
    # entities - TURQUOISE base - complement is ?????
    '290000':'00FFCC', # base
    '291000':'00FFCC', # add
    '292000':'33FFCC', # edit
    '293000':'33FF66', # delete
    '294000':'66FFCC', # search 
    '295000':'99FFCC', # view

    # locations
    '830000':'669933', # base
    '831000':'669966', # add
    '832000':'66CC66', # edit
    '833000':'66CC00', # delete
    '834000':'66CC33', # search 
    '835000':'66CC99', # view

    # files - NAVY base - complement is ????
    '180000':'330066', # base
    '181000':'330066', # add
    '182000':'330066', # edit
    '183000':'330066', # delete

     # articles
    '430000':'CC9966', # base
    '431000':'CC9966', # add
    '432000':'CCCC66', # edit
    '433000':'CCCC00', # delete
    '434000':'CCCC33', # search 
    '435000':'CCCC99', # view 
    '435001':'FFCC99', # print view 

   # news
    '305000':'FF0033', # base
    '305100':'FF0033', # add
    '305200':'FF0033', # edit
    '305300':'FF0033', # delete
    '305400':'FF0033', # search 
    '305500':'8C0000', # view
    '305501':'8C0000', # print view
       
    # jobs - GREEN base - complement is DEEP RED
    '250000':'669900', # base
    '251000':'669900', # add
    '252000':'666600', # edit
    '253000':'66FF66', # delete
    '254000':'66FF33', # search 
    '255000':'00CC66', # view    
    '255001':'336600', # print view    
    
    # pages
    '580000':'009900', # base
    '581000':'009933', # add
    '582000':'009966', # edit
    '583000':'00CC00', # delete
    '584000':'00FF00', # search 
    '585000':'00FF33', # view
    '585001':'00FF33', # print view          

    # photos - sky BLUE base with yellow compliment
    '990000':'1774F1', # base
    '990100':'2E82E3', # add
    '990200':'4690D5', # edit
    '990300':'5D9EC7', # delete
    '990400':'4682B9', # search 
    '990500':'2E79D1', # view 

    # photos sets
    '991000':'1374FF', # base
    '991100':'2582FF', # add
    '991200':'3890FF', # edit
    '991300':'4A9EFF', # delete
    '991400':'5DACFF', # search 
    '991500':'6FB9FF', # view   

    # stories
    '1060000':'FF33FF', # base
    '1060100':'FF33FF', # add
    '1060200':'DD77AA', # edit
    '1060300':'CC9980', # delete
    '1060400':'AADD2B', # search 
    '1060500':'99FF00', # view  

    # accounting
    '310000':'006666', # base
    '311000':'006666', # add
    '312000':'006633', # edit
    '313000':'006600', # delete
    '314000':'009900', # search 
    '315000':'009933', # view 
    '311220':'FF0000', # invoice adjusted    RED!!! 
    '312100':'339900', # general ledger added 
    '312200':'339900', # general ledger edited
    '312300':'339900', # general ledger deleted
    '312400':'339900', # general ledger searched
    '312500':'339900', # general ledger viewed
    '313300':'669933', # accounting entry deleted
    '313400':'669933', # accounting transaction deleted
    '315105':'669933', # acct entry table export    


    # payments - PINK ORANGE base - complement is ????
    '280000':'FF6666', # base
    '281000':'FF6666', # add
    '282000':'FF6666', # edit
    '283000':'FF6666', # delete
    '284000':'FF6666', # search 
    '285000':'FF6666', # view 
    '286000':'FF6666', # export 
    '282101':'FF6666', # Edit - Credit card approved 
    '282102':'FF6666', # Edit - Credit card declined 

    # make_payments - PINK ORANGE base - complement is ????
    '670000':'66CC00', # base
    '671000':'66CC00', # add
    '672000':'66CC33', # edit
    '673000':'66CC66', # delete
    '674000':'66FF00', # search 
    '675000':'66FF33', # view 
   
    # actions (Marketing Actions)
    '300000':'FF0033', # base
    '301000':'FF0033', # add
    '301100':'FF3333', # edit
    '303000':'FF0033', # delete
    '304000':'FF0033', # search 
    '305000':'FF0066', # view
    '301001':'FF0033', # submitted
    '301005':'FF0099', # resend

    # emails
    '130000':'CC3300', # base
    '131000':'CC3300', # add
    '132000':'CC3300', # edit
    '133000':'CC3300', # delete
    '134000':'CC3300', # search 
    '135000':'CC3300', # view
    '131100':'CC3366', # email send failure
    '131101':'CC3399', # email send success
    '131102':'CC33CC', # email send success - newsletter
    '130999':'FF0000', # email SPAM DETECTED!! (RED - this is important)

    # email_blocks
    '135000':'CC3300', # base
    '135100':'CC3300', # add
    '135300':'CC3300', # edit
    '135300':'CC3300', # delete
    '135400':'CC3300', # search 
    '135550':'CC3300', # view

    # rss
    '630000':'00FF00', # rss feed base
    '630500':'00FF00', # global rss feed
    '630543':'00FF33', # articles rss feed
    '630530':'00FFCC', # news rss feed
    '630560':'33FF99', # pages rss feed
    '630525':'00FF99', # jobs rss feed 
   
}

def get_color(event_id):
    """
        Gets the hex color of an event log based on the event id
        get_color('id')
    """
    if event_id in colors:
        return colors[event_id]
    else:
        return 'FFFFFF'
    
    return ''
    
    