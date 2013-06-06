INSERT INTO `forms_field` (`id`, `form_id`, `label`, `field_type`, `required`, `visible`, `choices`, `_order`, `field_function`, `position`, `default`)
VALUES
    (1, 1, 'First Name', 'CharField', 1, 1, '', 0, 'EmailFirstName', 2, ''),
    (2, 1, 'Last Name', 'CharField', 1, 1, '', 1, 'EmailLastName', 3, ''),
    (3, 1, 'Email address', 'EmailField', 1, 1, '', 2, NULL, 4, ''),
    (4, 1, 'Phone Number', 'CharField', 0, 1, '', 4, 'EmailPhoneNumber', 5, ''),
    (5, 1, 'Message', 'CharField/django.forms.Textarea', 1, 1, '', 3, NULL, 6, '');
