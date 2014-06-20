from tendenci.core.base.test import TestCase
from selenium.common.exceptions import NoSuchElementException


class MembershipTest(TestCase):

    def test_create_membership_entry(self):
        from tendenci.addons.memberships.models import MembershipDefault
        apps = MembershipDefault.objects.filter(status=True, status_detail='active')[:1]

        if not apps:
            return None

        self.browser.get('http://127.0.0.1:8000/memberships/%d/' % apps[0].id)
        form_fields = self.browser.find_elements_by_css_selector('.form-builder-wrap .form-field')

        for form_field in form_fields:

            try:
                label = form_field.find_element_by_css_selector('label')
                input_field = form_field.find_element_by_css_selector('input')
            except NoSuchElementException:
                continue  # on to the next one

            try:
                is_required = form_field.find_element_by_css_selector('div.label.required').get_attribute('class')
            except NoSuchElementException:
                is_required = False

            label = label.text
            if input_field.is_displayed():
                attr_type = input_field.get_attribute('type')

                if attr_type == 'text' and is_required:
                    if 'first name' in label.lower():
                        input_field.send_keys(self.user.first_name)
                    elif 'last name' in label.lower():
                        input_field.send_keys(self.user.last_name)
                    elif 'email' in label.lower():
                        input_field.send_keys(self.user.email)
                    else:
                        input_field.send_keys('blah')
                elif attr_type in ['checkbox', 'radio']:
                    input_field.click()

        self.save_screenshot()
        submit_btn = self.browser.find_element_by_css_selector('.form-builder-wrap input[type="submit"]')
        submit_btn.click()
        self.save_screenshot()
