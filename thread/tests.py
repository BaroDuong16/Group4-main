from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from thread.models import DiscussionThread

User = get_user_model()

class CreateThreadTestCase(TestCase):

    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')

        # URL for the createThread view
        self.create_thread_url = reverse('thread:create_thread')

    def test_create_thread_success(self):
        # Data for a valid thread
        data = {
            'thread_title': 'Test Thread',
            'thread_content': 'This is a test thread.',
        }

        # Send POST request to create a thread
        response = self.client.post(self.create_thread_url, data)

        # Check the thread was created
        self.assertEqual(DiscussionThread.objects.count(), 1)
        thread = DiscussionThread.objects.first()
        self.assertEqual(thread.thread_title, 'Test Thread')
        self.assertEqual(thread.thread_content, 'This is a test thread.')
        self.assertEqual(thread.created_by, self.user)

        # Check redirection to thread_list
        self.assertRedirects(response, reverse('thread:thread_list'))

    def test_create_thread_failure_invalid_data(self):
        # Data for an invalid thread (missing required fields)
        data = {
            'thread_title': '',
            'thread_content': '',
        }

        # Send POST request to create a thread
        response = self.client.post(self.create_thread_url, data)

        # Check the thread was not created
        self.assertEqual(DiscussionThread.objects.count(), 0)

        # Check the response renders the form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required.')

    def test_create_thread_unauthenticated_user(self):
        # Log out the user
        self.client.logout()

        # Data for a valid thread
        data = {
            'thread_title': 'Test Thread',
            'thread_content': 'This is a test thread.',
        }

        # Send POST request to create a thread
        response = self.client.post(self.create_thread_url, data)

        # Check the thread was not created
        self.assertEqual(DiscussionThread.objects.count(), 0)

        # Check redirection to login page
        self.assertRedirects(response, f"{reverse('login')}?next={self.create_thread_url}")
