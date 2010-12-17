INSERT INTO `corporate_memberships_corpfield` 
(`label`, `field_name`, `field_type`, `choices`, `field_layout`, `size`, `required`, `no_duplicates`, `visible`, 
`admin_only`, `help_text`, `default_value`, `css_class`) VALUES 
('Corporate Name','name','CharField','', '', 'm', 1, 1, 1, 0, '', '', '');

INSERT INTO `corporate_memberships_corpfield` 
(`label`, `field_name`, `field_type`, `choices`, `field_layout`, `size`, `required`, `no_duplicates`, `visible`, 
`admin_only`, `help_text`, `default_value`, `css_class`) VALUES 
('Address','address','CharField','', '', 'm', 1, 0, 1, 0, '', '', '');

INSERT INTO `corporate_memberships_corpfield` 
(`label`, `field_name`, `field_type`, `choices`, `field_layout`, `size`, `required`, `no_duplicates`, `visible`, 
`admin_only`, `help_text`, `default_value`, `css_class`) VALUES 
('Address2','address2','CharField','', '', 'm', 0, 0, 1, 0, '', '', '');

INSERT INTO `corporate_memberships_corpfield` 
(`label`, `field_name`, `field_type`, `choices`, `field_layout`, `size`, `required`, `no_duplicates`, `visible`, 
`admin_only`, `help_text`, `default_value`, `css_class`) VALUES 
('City','city','CharField','', '', 'm', 1, 0, 1, 0, '', '', '');

INSERT INTO `corporate_memberships_corpfield` 
(`label`, `field_name`, `field_type`, `choices`, `field_layout`, `size`, `required`, `no_duplicates`, `visible`, 
`admin_only`, `help_text`, `default_value`, `css_class`) VALUES 
('State','state','CharField','', '', 's', 1, 0, 1, 0, '', '', '');

INSERT INTO `corporate_memberships_corpfield` 
(`label`, `field_name`, `field_type`, `choices`, `field_layout`, `size`, `required`, `no_duplicates`, `visible`, 
`admin_only`, `help_text`, `default_value`, `css_class`) VALUES 
('Zip Code','zipcode','CharField','', '', 's', 1, 0, 1, 0, '', '', '');

INSERT INTO `corporate_memberships_corpfield` 
(`label`, `field_name`, `field_type`, `choices`, `field_layout`, `size`, `required`, `no_duplicates`, `visible`, 
`admin_only`, `help_text`, `default_value`, `css_class`) VALUES 
('Phone','phone','CharField','', '', 'm', 0, 0, 1, 0, '', '', '');

INSERT INTO `corporate_memberships_corpfield` 
(`label`, `field_name`, `field_type`, `choices`, `field_layout`, `size`, `required`, `no_duplicates`, `visible`, 
`admin_only`, `help_text`, `default_value`, `css_class`) VALUES 
('Website','website','CharField','', '', 'm', 0, 0, 1, 0, '', '', '');

INSERT INTO `corporate_memberships_corpfield` 
(`label`, `field_name`, `field_type`, `choices`, `field_layout`, `size`, `required`, `no_duplicates`, `visible`, 
`admin_only`, `help_text`, `default_value`, `css_class`) VALUES 
('Membership Type','corporate_membership_type','ChoiceField','', '1', 'm', 1, 0, 1, 0, '', '', '');

INSERT INTO `corporate_memberships_corpfield` 
(`label`, `field_name`, `field_type`, `choices`, `field_layout`, `size`, `required`, `no_duplicates`, `visible`, 
`admin_only`, `help_text`, `default_value`, `css_class`) VALUES 
('Payment Method','payment_method','ChoiceField','', '1', 'm', 1, 0, 1, 0, '', '', '');

INSERT INTO `corporate_memberships_corpfield` 
(`label`, `field_name`, `field_type`, `choices`, `field_layout`, `size`, `required`, `no_duplicates`, `visible`, 
`admin_only`, `help_text`, `default_value`, `css_class`) VALUES 
('Dues Representatives','dues_rep','CharField','', '', 'm', 1, 0, 1, 0, '', '', '');
