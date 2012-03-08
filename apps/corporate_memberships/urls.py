from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('corporate_memberships.views', 
    url(r'^$', 'search', name="corp_memb"),                 
    url(r"^(?P<slug>.*)/add/$", "add", name="corp_memb.add"),
    url(r"^add_conf/(?P<id>\d+)/$", "add_conf", name="corp_memb.add_conf"),
    url(r"^edit/(?P<id>\d+)/$", "edit", name="corp_memb.edit"),
    url(r"^edit_reps/(?P<id>\d+)/$", "edit_reps", name="corp_memb.edit_reps"),
    #url(r"^list/$", "list_view", name="corp_memb.list"),
    url(r"^search/$", "search", name="corp_memb.search"),
    url(r"^index/$", "index", name="corp_memb.index"),
    url(r'^roster/$', 'roster_search', name="corp_memb.roster_search"),
    url(r'^delete/(?P<id>\d+)/$', 'delete', name="corp_memb.delete"),
    url(r'^delete_rep/(?P<id>\d+)/$', 'delete_rep', name="corp_memb.delete_rep"),
    url(r"^renew/(?P<id>\d+)/$", "renew", name="corp_memb.renew"),
    url(r"^renew_conf/(?P<id>\d+)/$", "renew_conf", name="corp_memb.renew_conf"),
    url(r"^approve/(?P<id>\d+)/$", "approve", name="corp_memb.approve"),
    url(r"^(?P<id>\d+)/$", "view", name="corp_memb.view"),
    url(r'^reps_lookup/$', 'reps_lookup', name="corp_memb.reps_lookup"),
    
    # import
    url(r"^import/$", "corp_import", name="corp_import"),
    url(r"^import/upload-file/$", "corp_import", kwargs={'step':(1,'upload-file')}, 
        name="corp_memb_import_upload_file"),
    url(r"^import/map-fields/$", "corp_import", kwargs={'step':(2,'map-fields')}, 
        name="corp_memb_import_map_fields"),
    url(r"^import/preview/$", "corp_import", kwargs={'step':(3,'preview')}, 
        name="corp_memb_import_preview"),
    url(r"^import/confirm/$", "corp_import", kwargs={'step':(4,'confirm')}, 
        name="corp_memb_import_confirm"),
    url(r'^import/download-csv-template/$', 'download_csv_import_template', 
        name="corp_memb_import_download_template"),
    url(r'^import/download-invalid_records/$', 'corp_import_invalid_records_download', 
        name="corp_memb_import_download_invalid"),
        
    # export 
    url(r"^export/$", "corp_export", name="corp_export"),
    
    # reports
    url(r"^reports/corp_mems_over_time/$", "new_over_time_report", name="reports-corp-mems-over-time"),
    url(r"^reports/corp_mems_summary/$", "corp_mems_summary", name="reports-corp-mems-summary"),
)
