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

     # resumes
    '350000':'0099CC', # base
    '351000':'0099CC', # add
    '352000':'0099CC', # edit
    '353000':'0099CC', # delete
    '354000':'0099CC', # search
    '355000':'0099CC', # view
    '355001':'0099CC', # print view

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
    #'305000':'FF0066', # view (Duplicate of news base)
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

    # forms
    '587000':'33FFFF', # base
    '587100':'33FFE6', # add
    '587200':'33FFCC', # edit
    '587300':'33FFB3', # delete
    '587400':'33FF99', # search
    '587500':'33FF80', # view
    '587600':'33FF33', # export

    # directories
    '440000':'CCCC33', # base
    '441000':'CCCC33', # add
    '442000':'CCCC33', # edit
    '443000':'CCCC33', # delete
    '444000':'CCCC33', # search
    '445000':'CCCC33', # view
    '445001':'CCCC33', # print view
    '442210':'CCCC33', # renew

    # help files
    '1000000':'D11300', # base
    '1000100':'D52500', # add
    '1000200':'DA3800', # edit
    '1000300':'DF4A00', # delete
    '1000400':'E35D00', # search
    '1000500':'E86F00', # view

    # help file topics
    '1001000':'A20900', # base
    '1001100':'AC1300', # add
    '1001200':'B51C00', # edit
    '1001300':'B51C00', # delete
    '1001400':'C72E00', # search
    '1001500':'D13800', # view

    # impersonation
    #'1080000':'FF0000', # (Duplicate of membership entries base)

    # events
    '170000':'FF6600', # base
    '171000':'FF6600', # add
    '172000':'FFCC66', # edit
    '173000':'FF9900', # delete
    '174000':'FF9933', # search
    '175000':'FF9966', # view

    # event types
    '270000':'FFCC99', # base
    '271000':'FFCC99', # add
    '272000':'FFCC99', # edit
    '273000':'FFCC99', # delete
    '274000':'FFCC99', # search
    '275000':'FFCC99', # view

    # membership
    '470000':'333366', # base
    '471000':'333366', # add
    '472000':'333366', # edit
    '473000':'333366', # delete
    '474000':'333366', # search view
    '475000':'333366', # details view
    '475105':'333366', # export

    # membership type
    '475100':'333366', # add
    '475200':'333366', # edit
    '475300':'333366', # delete
    '475400':'333366', # search view
    '475500':'333366', # details view

    # membership application
    '650000':'FF0066', # base
    '651000':'FF0066', # add
    '652000':'FF3366', # edit
    '653000':'FF0099', # delete
    '654000':'FF3399', # search view
    '655000':'FF00CC', # details view

    # membership application fields
    '660000':'FF6633', # base
    '661000':'FF6633', # add
    '662000':'FF3366', # edit
    '663000':'FF9933', # delete
    '664000':'FF6666', # search view
    '665000':'FF9966', # details view

    # membership entries
    '1080000':'FF6633', # base
    '1081000':'FF6633', # add
    '1084000':'FF6633', # search view
    '1085000':'FF6633', # details view
    '1082101':'FF6633', # approved
    '1082102':'FF6633', # disapproved

    # membership notice
    '900000':'FFFF00', # base
    '901000':'FFDB00', # add
    '902000':'FFB600', # edit
    '903000':'FF9200', # delete
    '904000':'FF6D00', # search view
    '905000':'FF4900', # details view
    '906000':'FF2400', # print view

    # corporate membership
    '680000':'3300FF', # base
    '681000':'3300FF', # add
    '681001':'471DEF', # renew
    '682000':'1F85FF', # edit
    '682001':'4D29DF', # join approval
    '682002':'5233CF', # renewal approval
    '682003':'563BBF', # join dis-approval
    '682004':'7A6DAF', # renewal dis-approval
    '683000':'B0A8CF', # delete
    '689005':'47A0BF', # import

    # boxes
    '1100000':'5588AA', # base
    '1100100':'119933', # add
    '1100200':'EEDD55', # edit
    '1100300':'AA2222', # delete

    # homepage
    '100000':'7F0000', # view; tendenci color (maroon)

    ## Plugins ##

    # videos
    '1200000':'993355', # base
    '1200100':'119933', # add
    '1200200':'EEDD55', # edit
    '1200300':'AA2222', # delete
    '1200400':'CC55EE', # search
    '1200500':'55AACC', # detail

    # staff
    #'1080000':'EE7733', # base (Duplicate of membership entries base)
    '1080100':'119933', # add
    '1080200':'EEDD55', # edit
    '1080300':'AA2222', # delete
    '1080400':'CC55EE', # search
    '1080500':'55AACC', # detail

    # speakers
    '1070000':'99EE66', # base
    '1070100':'119933', # add
    '1070200':'EEDD55', # edit
    '1070300':'AA2222', # delete
    '1070400':'CC55EE', # search
    '1070500':'55AACC', # detail

    # quotes
    '150000':'FFEE44', # base
    '150100':'119933', # add
    '150200':'EEDD55', # edit
    '150300':'AA2222', # delete
    '154000':'CC55EE', # search
    '155000':'55AACC', # detail

    # case_studies (Duplicate of help files)
    #'1000000':'EE8877', # base
    #'1000100':'119933', # add
    #'1000200':'EEDD55', # edit
    #'1000300':'AA2222', # delete
    #'1000400':'CC55EE', # search
    #'1000500':'55AACC', # detail

    # attorneys
    '490000':'773300', # base
    '491000':'119933', # add
    '492000':'EEDD55', # edit
    '493000':'AA2222', # delete
    '494000':'CC55EE', # search
    '495000':'55AACC', # detail
    '496000':'886655', # special list index view

    # before and afters
    '1090000':'FFCCBB', # base
    '1090100':'119933', # add
    '1090200':'EEDD55', # edit
    '1090300':'AA2222', # delete
    '1090400':'CC55EE', # search
    '1090500':'55AACC', # detail

    # recurring payments - green
    '1120000':'1A7731', #base
    '1120100':'14A037', # add
    '1120200':'478256', # edit
    '1120300':'8FBA9A', # delete
    '1120400':'14E548', # search
    '1120500':'339B41', # disable

    # tendenci_guide
    '1002000':'A20900', # base
    '1002100':'119933', # add
    '1002200':'EEDD55', # edit
    '1002300':'AA2222', # delete
    '1002400':'CC55EE', # search
    '1002500':'55AACC', # detail

#    '':'', # base
#    '':'119933', # add
#    '':'EEDD55', # edit
#    '':'AA2222', # delete
#    '':'CC55EE', # search
#    '':'55AACC', # detail
}
