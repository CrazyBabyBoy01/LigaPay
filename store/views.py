import logging
import uuid

from django.contrib import messages
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.views.generic import TemplateView

from common.views import ContextMixin
from store.forms import SkinsOrderForm
from users.tasks import send_reset_email


logger = logging.getLogger(__name__)


class StoreSkinsView(ContextMixin, TemplateView):
    template_name = 'store/skins.html'
    title = 'Скины'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['skinorder_form'] = SkinsOrderForm()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            logger.warning(
                f"Неавторизованный пользователь попытался оформить заказ "
                f"с IP {request.META.get('REMOTE_ADDR')}"
            )
            return redirect('users:autorization')

        form = SkinsOrderForm(request.POST)
        form.request = self.request

        if form.is_valid():
            key = str(uuid.uuid4())
            purchase_type = 'образа' if form.cleaned_data.get('skin_name') else 'персонажа'
            item_name = form.cleaned_data.get('skin_name') or form.cleaned_data.get('char_name')
            mail_subject = 'Покупка с сайта Lol-Pay'
            html_message = render_to_string(
                'store/store_skins_email.html',
                {
                    'mail_subject': mail_subject,
                    'username': request.user.username,
                    'purchase_type': purchase_type,
                    'item_name': item_name,
                    'key': key,
                },
            )

            form.save()
            send_reset_email.delay(
                subject=mail_subject,
                message='',
                recipient_list=[request.user.email],
                html_message=html_message,
            )

            logger.info(
                f'Пользователь {request.user.username} успешно оформил заказ\
                    на {purchase_type} {item_name}.'
            )
            messages.success(request, 'Покупка совершена, письмо отправлено на почту')
        else:
            print('===> Ошибки формы:', form.errors)
            messages.error(request, 'Проверьте форму на ошибки')
            return render(request, self.template_name, {'skinorder_form': form})

        return redirect('main:index')
