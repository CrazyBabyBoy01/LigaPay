from django.contrib import auth, messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.shortcuts import HttpResponseRedirect, get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.generic import FormView, TemplateView
from django.views.generic.edit import CreateView, UpdateView

from common.views import ContextMixin
from users.forms import (
    CustomPasswordResetForm,
    EmailChangeForm,
    UserLoginForm,
    UserProfileForm,
    UserRegistrationForm,
)
from users.models import EmailVerification, User
from users.tasks import send_reset_email


# Create your views here.

TWO_WEEKS = 1209600


class UserLoginView(ContextMixin, LoginView):
    """
    Авторизация пользователя.

    Если не выбрано "Запомнить меня", сессия завершается при закрытии браузера.
    Иначе устанавливается срок жизни сессии в 2 недели.
    """

    form_class = UserLoginForm
    template_name = 'users/authorization.html'
    title = 'Авторизация'

    def form_valid(self, form):
        remember_me = bool(self.request.POST.get('remember_me'))

        if not remember_me:
            self.request.session.set_expiry(0)
        else:
            self.request.session.set_expiry(TWO_WEEKS)
        return super().form_valid(form)


class UserRegistrationView(SuccessMessageMixin, ContextMixin, CreateView):
    """
    Регистрация нового пользователя.

    После успешной регистрации:
    - создаётся объект User,
    - отправляется письмо для подтверждения email,
    - выводится сообщение об успехе и редирект на авторизацию.
    """

    model = User
    form_class = UserRegistrationForm
    template_name = 'users/registration.html'
    success_url = reverse_lazy('users:authorization')
    success_message = 'Вы успешно зарегистрированы! На вашу почту отправлено письмо с подтверждением.'
    title = 'Регистрация'


class UserProfileView(ContextMixin, UpdateView):
    """
    Редактирование профиля пользователя.
    Использует UserProfileForm. После сохранения возвращает на страницу профиля.
    """

    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    title = 'Профиль'
    background_image = '/static/deps/images/287bff71fe2c1293dbd1be864fb6537f.jpg'

    def get_success_url(self):
        return reverse_lazy('users:profile', args=(self.object.id,))


class EmailVerificationView(ContextMixin, TemplateView):
    """
    Подтверждение email пользователя.

    - Если это первичная верификация — активирует email.
    - Если это смена email — обновляет адрес.
    - При ошибке или истёкшем коде → редирект на главную.
    """

    title = 'Подтверждение электронной почты'
    template_name = 'users/email_verification.html'
    background_image = '/static/deps/images/SB_Riven.jpg'

    def get(self, request, *args, **kwargs):
        code = kwargs['code']
        user = get_object_or_404(User, email=kwargs['email'])

        if not user.is_verified_email and self.verify_main_email(user, code):
            return super().get(request, *args, **kwargs)
        if self.change_email(user, code):
            return super().get(request, *args, **kwargs)
        return HttpResponseRedirect(reverse('main:index'))

    def verify_main_email(self, user, code):
        """Подтверждает основной email."""
        verification = (
            EmailVerification.objects.select_related('user').filter(user=user, code=code).first()
        )
        if verification and not verification.is_expired():
            user.is_verified_email = True
            user.save()
            return True
        return False

    def change_email(self, user, code):
        """Подтверждает смену email."""
        if user.email_change_token == code and user.new_email:
            user.email = user.new_email
            user.new_email = None
            user.email_change_token = None
            user.save()
            return True
        return False

    def reset_email_verification(self, user):
        """Сбрасывает статус подтверждения email (для админа или отзыва верификации)."""
        user.is_verified_email = False
        user.save()


class ChangeEmailView(FormView):
    """
    Запрос смены email.

    1. Пользователь вводит новый email.
    2. На старый email отправляется ссылка с подтверждением.
    3. После перехода по ссылке email обновляется (ConfirmEmailChangeView).
    """

    template_name = 'users/email_reset.html'
    form_class = EmailChangeForm

    def form_valid(self, form):
        new_email = form.cleaned_data['new_email']
        user = self.request.user

        confirm_url = self.generate_confirmation_url(user, new_email)

        self.send_confirmation_email(user, confirm_url)

        messages.success(self.request, 'Ссылка для подтверждения отправлена на ваш старый email.')

        return redirect('users:email_reset_done')

    def generate_confirmation_url(self, user, new_email):
        """Генерирует уникальную ссылку для подтверждения смены email."""
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        return self.request.build_absolute_uri(
            reverse(
                'users:confirm_email_change',
                kwargs={'uidb64': uid, 'token': token, 'new_email': new_email},
            )
        )

    def send_confirmation_email(self, user, confirm_url):
        """Отправляет письмо с подтверждением на текущий email пользователя."""
        subject = 'Подтверждение смены электронной почты'
        message = f'Перейдите по ссылке, чтобы подтвердить изменение email: {confirm_url}'
        recipient_list = [user.email]
        transaction.on_commit(lambda: send_reset_email.delay(subject, message, recipient_list))


class ConfirmEmailChangeView(View):
    """
    Подтверждение смены email.

    1. Декодирует uid и получает пользователя.
    2. Проверяет валидность токена.
    3. Если всё ок → обновляет email и сообщает об успехе.
    """

    def get(self, request, uidb64, token, new_email):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if self.verify_token(user, token):
            self.apply_new_email(user, new_email)
            messages.success(request, 'Ваш email успешно изменен!')
        else:
            messages.error(request, 'Ссылка для подтверждения недействительна.')
        return redirect('users:email_reset_complete')

    def verify_token(self, user, token):
        """Проверяет валидность токена для пользователя."""
        return bool(user is not None and default_token_generator.check_token(user, token))

    def apply_new_email(self, user, new_email):
        """Применяет новый email к пользователю."""
        if user and new_email:
            user.email = new_email
            user.save()
            return True
        return False


class EmailResetCompleteView(TemplateView):
    """Страница: email успешно изменён."""

    template_name = 'users/email_reset_complete.html'
    title = 'Email reset complete'


class EmailResetDoneView(TemplateView):
    """Страница: ссылка для подтверждения отправлена."""

    template_name = 'users/email_reset_done.html'
    title = 'Email reset done'


class CustomPasswordResetView(PasswordResetView):
    """Сброс пароля с кастомным шаблоном формы и письма."""

    form_class = CustomPasswordResetForm
    template_name = 'users/password_reset.html'  # Используйте ваш шаблон
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('users:password_reset_done')


def logout(request):
    """Выход пользователя из системы."""
    auth.logout(request)
    return HttpResponseRedirect(reverse('main:index'))
