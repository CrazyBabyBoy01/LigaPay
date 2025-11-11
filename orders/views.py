import logging

from django.apps import apps
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.html import escape
from django.views import View
from django.views.generic import ListView

from chat.utils import get_or_create_chat, send_chat_event
from common.views import ContextMixin
from orders.services import BuyerNotFound, NotEnoughFunds, WalletNotFound
from products.forms import PurchaseForm

from .models import Order, Review


logger = logging.getLogger(__name__)
User = get_user_model()


class CreateOrderView(LoginRequiredMixin, View):
    """Создание заказа и попытка оплаты"""

    def _get_product(self, model_name, product_id):
        model = apps.get_model('products', model_name)
        if not model:
            return None
        try:
            product = model.objects.select_for_update().select_related('seller').get(id=product_id)
            return product
        except model.DoesNotExist:
            return None

    def post(self, request, model_name, product_id):
        logger.info(
            'Попытка создания заказа. Пользователь=%s, product_id=%s', request.user.id, product_id
        )
        form = PurchaseForm(request.POST)

        if not form.is_valid():
            logger.warning(
                'Ошибка валидации формы при создании заказа. User=%s, data=%s',
                request.user.id,
                request.POST,
            )
            messages.error(request, 'Некорректные данные!')
            return redirect('users:profile', pk=request.user.pk)
        logger.info(f'Данные формы: {form.cleaned_data}')
        amount = form.cleaned_data.get('amount', 1)
        logger.info('Форма успешно обработана. User=%s, amount=%s', request.user.id, amount)
        try:
            with transaction.atomic():
                product = self._get_product(model_name, product_id)
                if not product:
                    logger.warning(
                        'Товар не найден. User=%s, model=%s, product_id=%s',
                        request.user.id,
                        model_name,
                        product_id,
                    )
                    messages.error(request, 'Товар не найден!')
                    return JsonResponse({'success': False, 'message': 'Товар не найден!'})
                has_quantity = hasattr(product, 'quantity')
                if has_quantity and amount > product.quantity:
                    logger.warning(
                        'Недостаточно товара. User=%s, Product=%s, requested=%s, available=%s',
                        request.user.id,
                        product.id,
                        amount,
                        product.quantity,
                    )
                    messages.error(request, 'Недостаточное количество товара в наличии!')
                    return JsonResponse(
                        {'success': False, 'message': 'Недостаточное количество товара в наличии!'}
                    )
                total_price = product.price * amount
                order = Order.objects.create(
                    user=request.user,
                    seller=product.seller,
                    content_type=ContentType.objects.get_for_model(product),
                    object_id=product.id,
                    price=total_price,
                    description=product.description,
                    amount=amount,
                )
                logger.info(
                    'Создан заказ. Order=%s, User=%s, Seller=%s',
                    order.id,
                    request.user.id,
                    product.seller.id,
                )
                try:
                    order.hold_payment()
                    if hasattr(product, 'quantity'):
                        product.quantity -= amount
                        product.save()
                    logger.info('Оплата зарезервирована. Order=%s', order.id)
                except NotEnoughFunds:
                    logger.warning('Недостаточно средств. Order=%s, User=%s', order.id, request.user.id)
                    order.delete()
                    return JsonResponse({'success': False, 'message': 'Недостаточно средств.'})
                except WalletNotFound:
                    logger.warning('Кошелек не найден. Order=%s, User=%s', order.id, request.user.id)
                    order.delete()
                    return JsonResponse({'success': False, 'message': 'У пользователя нет кошелька.'})
                logger.info('Заказ успешно создан и оплата зарезервирована. Order=%s', order.id)
                chat_room = get_or_create_chat(request.user, product.seller)
                message_text = (
                    f'✅ Покупатель <span class="username">{escape(request.user.username)}</span> создал <span class="order-id">заказ #{order.id}</span>.'
                    f'{escape(product.title)}, {amount} шт.'
                    f'<span class="username">{escape(request.user.username)}</span>, не забудьте потом нажать кнопку '
                    f'«Подтвердить покупку».'
                )
                send_chat_event(chat_room, order, message_text, request, event_type='order_created')

                if request.META.get('HTTP_X_REQUESTED_WITH') != 'XMLHttpRequest':
                    messages.success(request, 'Заказ создан! Подтвердите покупку в чате. ✅')

                return JsonResponse(
                    {'success': True, 'message': 'Заказ создан! Подтвердите покупку в чате.'}
                )

        except ValueError as e:
            logger.error(
                'Неизвестная ошибка при создании заказа. User=%s, error=%s', request.user.id, str(e)
            )
            return JsonResponse({'success': False, 'message': str(e)})
        except Exception as e:
            logger.error(
                'Непредвиденная ошибка при создании заказа. User=%s, error=%s', request.user.id, str(e)
            )
            return JsonResponse({'success': False, 'message': 'Произошла ошибка при оформлении заказа!'})


class ConfirmOrderView(View):
    """Подтверждение оплаты заказа"""

    def post(self, request, order_id):
        logger.info('Попытка подтверждения заказа. Покупатель=%s,order_id=%s', request.user.id, order_id)
        try:
            with transaction.atomic():
                order = get_object_or_404(Order, id=order_id, user=request.user)

                if order.status != 'pending':
                    logger.warning(
                        'Этот заказ уже подтвержден или отменен. User=%s, order_id=%s',
                        request.user.id,
                        order_id,
                    )
                    return JsonResponse(
                        {'success': False, 'message': 'Этот заказ уже подтвержден или отменен.'}
                    )

                try:
                    order.process_payment()
                    logger.info(
                        'Заказ подтвержден. Покупатель=%s,order_id=%s,Продавец=%s',
                        request.user.id,
                        order_id,
                        order.seller.id,
                    )
                except NotEnoughFunds:
                    logger.warning(
                        'У покупателя недостаточно средств. Покупатель=%s, order_id=%s',
                        request.user.id,
                        order_id,
                    )
                    return JsonResponse({'success': False, 'message': 'Недостаточно средств.'})
                except WalletNotFound:
                    logger.warning(
                        'У покупателя нет кошелька. Покупатель=%s, order_id=%s',
                        request.user.id,
                        order_id,
                    )
                    return JsonResponse({'success': False, 'message': 'У пользователя нет кошелька.'})

                chat_room = get_or_create_chat(request.user, order.seller)

                if not chat_room:
                    logger.warning(
                        'Покупка подтверждена, но чат не найден. Покупатель=%s, order_id=%s',
                        request.user.id,
                        order_id,
                    )
                    return JsonResponse(
                        {'success': True, 'message': 'Покупка подтверждена, но чат не найден.'}
                    )
                message_text = (
                    f'✅ <span class="username">{escape(request.user.username)}</span> оплатил '
                    f'<span class="order-id">заказ #{order.id}</span> и отправил деньги продавцу '
                    f'<span class="username">{escape(order.seller.username)}</span>.'
                )
                send_chat_event(chat_room, order, message_text, event_type='order_confirmed')
            logger.info(
                'Заказ подтвержден и событие отправлено. Покупатель=%s,order_id=%s,Продавец=%s',
                request.user.id,
                order_id,
                order.seller.id,
            )
            return JsonResponse(
                {
                    'success': True,
                    'message': 'Покупка подтверждена и оплачена!',
                    'reload': True,
                    'show_review': True,
                }
            )
        except ValueError as e:
            logger.error(
                'Неизвестная ошибка при подтверждении заказа. User=%s, error=%s', request.user.id, str(e)
            )
            return JsonResponse({'success': False, 'message': str(e)})
        except Exception as e:
            logger.error(
                'Непредвиденная ошибка при подтверждении заказа. User=%s, error=%s',
                request.user.id,
                str(e),
            )
            return JsonResponse({'success': False, 'message': 'Произошла ошибка при оформлении заказа!'})


class CancelOrderView(LoginRequiredMixin, View):
    """Отмена оплаты заказа"""

    def post(self, request, order_id):
        logger.info('Попытка отмены заказа. Продавец=%s,order_id=%s', request.user.id, order_id)
        try:
            with transaction.atomic():
                order = get_object_or_404(Order.objects.select_related('user', 'seller'), id=order_id)

                if request.user != order.seller:
                    logger.warning(
                        'Вы не можете отменить этот заказ. Продавец=%s, order_id=%s',
                        request.user.id,
                        order_id,
                    )
                    return JsonResponse(
                        {'success': False, 'message': 'Вы не можете отменить этот заказ.'}
                    )

                if order.status != 'pending':
                    logger.warning(
                        'Нельзя отменить завершённый заказ. Продавец=%s, order_id=%s',
                        request.user.id,
                        order_id,
                    )
                    return JsonResponse(
                        {'success': False, 'message': 'Нельзя отменить завершённый заказ.'}
                    )

                try:
                    order.refund()
                    logger.info(
                        'Заказ отменен и деньги возвращены покупателю.Продавец=%s,покупатель= %s,order_id=%s',
                        request.user.id,
                        order.user.id,
                        order_id,
                    )
                except BuyerNotFound:
                    logger.warning(
                        'У заказа не указан покупатель. Продавец=%s, order_id=%s',
                        request.user.id,
                        order_id,
                    )
                    return JsonResponse({'success': False, 'message': 'У заказа не указан покупатель'})
                except WalletNotFound:
                    logger.warning(
                        'У пользователя . Продавец=%s, order_id=%s',
                        request.user.id,
                        order_id,
                    )
                    return JsonResponse({'success': False, 'message': 'У пользователя нет кошелька.'})
                except NotEnoughFunds:
                    logger.warning(
                        'Возврат невозможен. Продавец=%s, order_id=%s',
                        request.user.id,
                        order_id,
                    )
                    return JsonResponse({'success': False, 'message': 'Возврат невозможен'})
                chat_room = get_or_create_chat(order.user, order.seller)
                if not chat_room:
                    logger.warning(
                        'Покупка отменена, но чат не найден.. Продавец=%s, order_id=%s',
                        request.user.id,
                        order_id,
                    )
                    return JsonResponse({'success': True, 'message': 'Заказ отменён, но чат не найден.'})
                message_text = (
                    f'❌ <span class="username">{escape(order.seller.username)}</span> отклонил '
                    f'<span class="order-id">заказ #{order.id}</span>.'
                )
                send_chat_event(chat_room, order, message_text)
            logger.info(
                'Заказ успешно отклонён и событие отправлено.Продавец=%s,покупатель= %s,order_id=%s',
                request.user.id,
                order.user.id,
                order_id,
            )
            return JsonResponse({'success': True, 'message': 'Заказ успешно отклонён.'})
        except ValueError as e:
            logger.error(
                'Неизвестная ошибка при отмене заказа. User=%s, error=%s', request.user.id, str(e)
            )
            return JsonResponse({'success': False, 'message': str(e)})
        except Exception as e:
            logger.error(
                'Непредвиденная ошибка при отмене заказа. User=%s, error=%s',
                request.user.id,
                str(e),
            )
            return JsonResponse({'success': False, 'message': 'Произошла ошибка при оформлении заказа!'})


class OrderListView(LoginRequiredMixin, ContextMixin, ListView):
    """Вывод списка заказов пользователя"""

    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    title = 'История покупок'

    def get_queryset(self):
        """Фильтруем заказы только для текущего пользователя"""
        return (
            Order.objects.filter(user=self.request.user)
            .select_related('user', 'seller')
            .order_by('-created_at')
        )


class SaleListView(LoginRequiredMixin, ContextMixin, ListView):
    """Вывод списка продаж пользователя"""

    model = Order
    template_name = 'orders/sale_list.html'
    context_object_name = 'sales'
    title = 'История продаж'

    def get_queryset(self):
        """Фильтруем заказы, где текущий пользователь является продавцом"""
        return (
            Order.objects.filter(seller=self.request.user)
            .select_related('user', 'seller')
            .order_by('-created_at')
        )


class ReviewCreateView(LoginRequiredMixin, View):
    """Отзывы"""

    def post(self, request):
        try:
            logger.info(
                'Попытка оставить отзыв. user=%s, raw_order_id=%s',
                request.user.id,
                request.POST.get('order_id'),
            )
            order_id = int(request.POST.get('order_id'))
        except (TypeError, ValueError):
            logger.warning(
                'Некорректный ID заказа. user=%s, raw_order_id=%s',
                request.user.id,
                request.POST.get('order_id'),
            )
            messages.error(request, 'Некорректный ID заказа.')
            return redirect('main:index')

        order = get_object_or_404(Order.objects.select_related('user', 'seller'), id=order_id)

        if order.user != request.user:
            logger.warning(
                'Пользователь не может оставить отзыв. user=%s, order_id=%s', request.user.id, order.id
            )
            messages.error(request, 'Вы не можете оставить отзыв к этому заказу.')
            return redirect('orders:my_orders')

        if hasattr(order, 'review'):
            logger.warning(
                'Повторная попытка оставить отзыв. user=%s, order_id=%s', request.user.id, order.id
            )
            messages.warning(request, 'Вы уже оставили отзыв для этого заказа.')
            return redirect('orders:my_orders')

        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '').strip()

        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise ValueError
        except (TypeError, ValueError):
            logger.warning(
                'Некорректная оценка. user=%s, order_id=%s, rating=%s', request.user.id, order.id, rating
            )
            messages.error(request, 'Оценка должна быть числом от 1 до 5.')
            return redirect('orders:my_orders')


        Review.objects.create(
            order=order,
            author=request.user,
            seller=order.seller,
            rating=rating,
            comment=comment,
        )
        logger.info('Отзыв создан. user=%s, order_id=%s, rating=%s', request.user.id, order.id, rating)
        messages.success(request, 'Спасибо! Ваш отзыв сохранён.')
        return redirect('main:index')
