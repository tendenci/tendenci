import logging

from django.test import Client, TestCase
from django.contrib.auth.models import User

from tendenci.apps.navs.models import Nav, NavItem


handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)


logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class NavAdminInlineTest(TestCase):

    def setUp(self):
        self.nav = Nav(title="Test Nav")
        self.nav.save()
        NavItem.objects.create(label="Test Item 1", nav=self.nav, level=0, position=0)
        NavItem.objects.create(label="Test Item 2", nav=self.nav, level=0, position=1)
        NavItem.objects.create(label="Test Item 3", nav=self.nav, level=0, position=2)
        self.add_url = '/admin/navs/nav/add/'
        self.change_url = '/admin/navs/nav/%i/' % self.nav.id

        self.client = Client()
        username = 'tester'
        email = 'test@test.com'
        password = 'test'
        User.objects.create_superuser(username, email, password)
        result = self.client.login(username=username, password=password)
        self.assertEqual(result, True)

    def tearDown(self):
        self.client.logout()

    def test_nav_add(self):
        logger.info('Testing Nav addition via admin page.')
        data = {
            'navitem_set-TOTAL_FORMS': 3,
            'navitem_set-INITIAL_FORMS': 0,
            'navitem_set-MAX_NUM_FORMS': 0,
            '_save': 'Save',
            'title': "Admin Nav",
            'description': "",
            'status_detail': "active",
            'allow_anonymous_view': True,
            'user_perms': [],
            'group_perms': [],
            'navitem_set-0-level': 0,
            'navitem_set-0-position': 0,
            'navitem_set-0-label': "Main Item 1",
            'navitem_set-0-title': "",
            'navitem_set-0-css': "",
            'navitem_set-0-page': "",
            'navitem_set-0-url': "",
            'navitem_set-0-new_window': False,
            'navitem_set-1-level': 1,
            'navitem_set-1-position': 1,
            'navitem_set-1-label': "Item 1 Child",
            'navitem_set-1-title': "",
            'navitem_set-1-css': "",
            'navitem_set-1-page': "",
            'navitem_set-1-url': "",
            'navitem_set-1-new_window': False,
            'navitem_set-2-level': 0,
            'navitem_set-2-position': 2,
            'navitem_set-2-label': "Main Item 2",
            'navitem_set-2-title': "",
            'navitem_set-2-css': "",
            'navitem_set-2-page': "",
            'navitem_set-2-url': "",
            'navitem_set-2-new_window': False,
        }
        response = self.client.post(self.add_url, data)
        self.assertEqual(response.status_code, 302)

        logger.info('Testing if Nav is added')
        self.assertEqual(len(Nav.objects.filter(title__exact='Admin Nav')), 1)
        nav = Nav.objects.get(title__exact='Admin Nav')

        logger.info('Testing if NavItems are added')
        self.assertEqual(len(NavItem.objects.filter(nav=nav)), 3)
        logger.info('Testing if Nav has the correct number of top items.')
        self.assertEqual(len(nav.top_items), 2)

        logger.info('Testing if NavItem has a child')
        navItem = NavItem.objects.get(label__exact='Main Item 1')
        self.assertEqual(len(navItem.children), 1)
        logger.info('Complete.')

    def test_nav_change(self):
        logger.info('Verifying the existence of Nav to be edited')
        response = self.client.get(self.change_url)
        self.assertEqual(response.status_code, 200)

        logger.info('Testing the number of top items for Nav before edit')
        self.assertEqual(len(self.nav.top_items), 3)

        logger.info('Testing Nav edit via admin page.')
        data = {
            'navitem_set-TOTAL_FORMS': 3,
            'navitem_set-INITIAL_FORMS': 3,
            'navitem_set-MAX_NUM_FORMS': 0,
            '_save': 'Save',
            'title': "Test Nav",
            'description': "",
            'status_detail': "active",
            'allow_anonymous_view': True,
            'user_perms': [],
            'group_perms': [],
            'navitem_set-0-id': 1,
            'navitem_set-0-level': 0,
            'navitem_set-0-position': 0,
            'navitem_set-0-label': "Test Item 1",
            'navitem_set-0-title': "",
            'navitem_set-0-css': "",
            'navitem_set-0-page': "",
            'navitem_set-0-url': "",
            'navitem_set-0-new_window': False,
            'navitem_set-1-id': 2,
            'navitem_set-1-level': 1,
            'navitem_set-1-position': 1,
            'navitem_set-1-label': "Test Item 2",
            'navitem_set-1-title': "",
            'navitem_set-1-css': "",
            'navitem_set-1-page': "",
            'navitem_set-1-url': "",
            'navitem_set-1-new_window': False,
            'navitem_set-2-id': 3,
            'navitem_set-2-level': 0,
            'navitem_set-2-position': 2,
            'navitem_set-2-label': "Test Item 3",
            'navitem_set-2-title': "",
            'navitem_set-2-css': "",
            'navitem_set-2-page': "",
            'navitem_set-2-url': "",
            'navitem_set-2-new_window': False,
        }
        response = self.client.post(self.change_url, data)
        self.assertEqual(response.status_code, 302)

        logger.info('Testing the number of top items for Nav after edit')
        self.assertEqual(len(self.nav.top_items), 2)

        logger.info('Testing if the other NavItem became a child')
        navItem = NavItem.objects.get(label__exact='Test Item 1')
        self.assertEqual(len(navItem.children), 1)
        logger.info('Complete.')
