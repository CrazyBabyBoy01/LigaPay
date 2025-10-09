from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.utils.timezone import now, timedelta

from users.middleware import UpdateLastActivityMiddleware


User = get_user_model()


class UpdateLastActivityMiddlewareTestCase(TestCase):
    def test_middleware_updates_last_activity_for_authenticated_user(self):
        """
        Проверяет, что middleware обновляет поле last_activity
        у аутентифицированного пользователя, если прошло более 30 секунд.
        """
        user = User.objects.create_user(
            username='newuser',
            email='test@example.com',
            password='pass1234',
            last_activity=now() - timedelta(seconds=31),
        )

        request = RequestFactory().get('/')
        request.user = user

        middleware = UpdateLastActivityMiddleware(lambda req: HttpResponse('OK'))
        response = middleware(request)

        user.refresh_from_db()
        self.assertGreaterEqual(user.last_activity, now() - timedelta(seconds=1))
        self.assertEqual(response.status_code, 200)
