## Mobile Functionality

When setting up your mobile layout, you can select to show the mobile content using the code below (a mobile stylesheet is included in the example)   
   
    {% if request.mobile %}
        <link rel="stylesheet" href="{{ THEME_URL }}media/css/styles-mobile.css" type="text/css" />
    {% endif %}   

That same code can be used to include a separate layout, separate navigation, or anything else that you may want to display to mobile viewers but not to desktop browsers.


To take advantage of the cookie opt-out for mobile viewers who want to view the full site, first load the mobile tags at the top of the template:
    
    {% load mobile_tags %}
 
To show the link to mobile theme viewers to view full site
 
    {% if request.mobile %}
        {% toggle_mobile_link request.get_full_path "View full site" %}
    {% endif %}
 
To show the view mobile site link to mobile browser viewers who previously opted out
 
    {% if request.mobile_browser and not request.mobile %}
        {% toggle_mobile_link request.get_full_path "View mobile site" %}
    {% endif %}
    
The placement of these links, as well as the text of the link is customizable.

## Mobile Browsers Supported

The following mobile browsers are supported:

- iPad
- iPhone
- iPod
- Android
- Opera Mini
- Blackberry
- Droid
- IEMobile
- EudoraWeb
- Fennec
- Minimo
- NetFront
- Polaris
- HTC_Dream
- HTC Hero
- HTC-ST7377
- Kindle
- LG-LX550
- LX265
- Nokia
- Palm
- MOT-V9mm
- SEC-SGHE900
- SAMSUNG-SGH-A867
- SymbianOS
- DoCoMo
- ZuneHD
- ReqwirelessWeb
- SEJ001

