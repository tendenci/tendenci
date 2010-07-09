# colors from schipul_codebase_dev\cb\eventlogs\cb_eventlogs_hex.asp
# colors = { 'event_id':'hex color' }
colors = {
    # profiles
    '121000':'3300FF', # add
    '122000':'3333FF', # edit
    '123000':'3366FF', # delete
    '124000':'3366FF', # search 
    '125000':'3399FF', # view

    # login
    '125200':'66CCFF',
        
    # articles
    '431000':'CC9966', # add
    '432000':'CCCC66', # edit
    '433000':'CCCC00', # delete
    '434000':'CCCC33', # search 
    '435000':'CCCC99', # view 

    # entities
    '291000':'00FFCC', # add
    '292000':'33FFCC', # edit
    '293000':'33FF66', # delete
    '294000':'66FFCC', # search 
    '295000':'99FFCC', # view

    # files
    '181000':'330066', # add
    '182000':'330066', # edit
    '183000':'330066', # delete

    # news
    '305100':'FF0033', # add
    '305200':'FF0033', # edit
    '305300':'FF0033', # delete
    '305400':'FF0033', # search 
    '305500':'8C0000', # view

    # pages
    '581000':'009933', # add
    '582000':'009966', # edit
    '583000':'00CC00', # delete
    '584000':'00FF00', # search 
    '585000':'00FF33', # view       

    # photos
    '990100':'2E82E3', # add
    '990200':'4690D5', # edit
    '990300':'5D9EC7', # delete
    '990400':'4682B9', # search 
    '990500':'2E79D1', # view 

    # photos sets
    '991100':'2582FF', # add
    '991200':'3890FF', # edit
    '991300':'4A9EFF', # delete
    '991400':'5DACFF', # search 
    '991500':'6FB9FF', # view   

    # stories
    '1060100':'FF33FF', # add
    '1060200':'DD77AA', # edit
    '1060300':'CC9980', # delete
    '1060400':'AADD2B', # search 
    '1060500':'99FF00', # view  

    # groups
    '161000':'339999', # add
    '162000':'339999', # edit
    '163000':'339999', # delete
    '164000':'339999', # search 
    '165000':'339999', # view    

    # group relationship
    '221000':'00CCFF', # add
    '222000':'00CCFF', # edit
    '223000':'00CCFF', # delete
    '224000':'00CCFF', # search 
    '225000':'00CCFF', # view   
    
    # locations
    '831000':'669966', # add
    '832000':'66CC66', # edit
    '833000':'66CC00', # delete
    '834000':'66CC33', # search 
    '835000':'66CC99', # view

    # contacts
    '587100':'33FFE6', # add
    '587200':'33FFCC', # edit
    '587300':'33FFB3', # delete
    '587400':'33FF99', # search 
    '587500':'33FF80', # view

    # jobs
    '251000':'669900', # add
    '252000':'666600', # edit
    '253000':'66FF66', # delete
    '254000':'66FF33', # search 
    '255000':'00CC66', # view    
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
    
    