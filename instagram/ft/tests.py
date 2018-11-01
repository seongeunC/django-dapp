from django.test import LiveServerTestCase
from selenium import webdriver


class NewVisitorTest(LiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(1)

    def tearDown(self):
        self.browser.quit()

    def test_root_url_redirect_to_post_list_view(self):
        self.browser.get(self.live_server_url)

        post_list_url = '/post/'
        self.assertEqual(
            self.browser.current_url,
            self.live_server_url + post_list_url
        )
