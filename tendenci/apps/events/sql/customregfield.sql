INSERT INTO `events_customregfield` (`form_id`, `label`, `field_type`, `map_to_field`, `required`, `visible`, `choices`, `position`, `default`, `display_on_roster`)
VALUES
    (1, 'First Name', 'CharField', 'first_name', 1, 1, '', 1, '', 1);
INSERT INTO `events_customregfield` (`form_id`, `label`, `field_type`, `map_to_field`, `required`, `visible`, `choices`, `position`, `default`, `display_on_roster`)
VALUES
    (1, 'Last Name', 'CharField', 'last_name', 1, 1, '', 2, '', 1);
INSERT INTO `events_customregfield` (`form_id`, `label`, `field_type`, `map_to_field`, `required`, `visible`, `choices`, `position`, `default`, `display_on_roster`)
VALUES
    (1, 'Email', 'EmailField', 'email', 1, 1, '', 3, '', 0);
INSERT INTO `events_customregfield` (`form_id`, `label`, `field_type`, `map_to_field`, `required`, `visible`, `choices`, `position`, `default`, `display_on_roster`)
VALUES
    (1, 'Title', 'CharField', 'position_title', 0, 1, '', 4, '', 1);
INSERT INTO `events_customregfield` (`form_id`, `label`, `field_type`, `map_to_field`, `required`, `visible`, `choices`, `position`, `default`, `display_on_roster`)
VALUES
    (1, 'Company', 'CharField', 'company_name', 0, 1, '', 5, '', 1);
INSERT INTO `events_customregfield` (`form_id`, `label`, `field_type`, `map_to_field`, `required`, `visible`, `choices`, `position`, `default`, `display_on_roster`)
VALUES
    (1, 'Comments', 'CharField/django.forms.Textarea', '', 0, 1, '', 7, '', 0);