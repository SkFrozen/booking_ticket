from django.test import TestCase

from ..models import User
from ..tasks import delete_user_task, send_register_email_task


class TestUsersTasks(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="test",
            email="test@test.com",
            password="test",
            is_active=False,
        )
        cls.domain = "test.com"
        cls.task = send_register_email_task.apply(args=[cls.domain, cls.user.id])

    def test_send_register_email_task(self):
        response = self.task.get()

        self.assertEqual(response, True)

    def test_delete_user_task(self):
        delete_user_task.apply(args=[self.user.id])

        try:
            user = User.objects.get(id=self.user.id)
        except User.DoesNotExist:
            user = None

        self.assertEqual(user, None)
