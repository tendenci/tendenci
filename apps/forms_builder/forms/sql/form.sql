-- site settings for the forms module

-- DELETE all settings under this module
DELETE FROM site_settings_setting WHERE scope = 'module' AND scope_category = 'forms';


-- INSERT the settings
INSERT IGNORE INTO site_settings_setting (name, label, description, data_type, value, default_value, input_type, input_value, client_editable, store, update_dt, updated_by, scope, scope_category, parent_id) VALUES ('enabled','Enabled','Module is enabled or not.','boolean','true','true','select','true,false',0,1,NOW(),'','module','forms',0);

INSERT IGNORE INTO site_settings_setting (name, label, description, data_type, value, default_value, input_type, input_value, client_editable, store, update_dt, updated_by, scope, scope_category, parent_id) VALUES ('label','Label','The name of the module.','string','Forms','Forms','text','',0,1,NOW(),'','module','forms',0);
