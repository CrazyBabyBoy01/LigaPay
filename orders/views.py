import logging

from channels.consumer import async_to_sync
from channels.layers import get_channel_layer
from chat.models import ChatMessage, ChatRoom
from common.views import ContextMixin
from django.apps import apps
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.html import escape
from django.views import View
from django.views.generic import ListView
from products.forms import PurchaseForm
from products.models import (
    AccountService,
    BattlePassService,
    BoostService,
    DonationService,
    GeneralService,
    OtherService,
    QualificationService,
    RPService,
    ServerBasedService,
    TrainingService,
)

from .models import Order


logger = logging.getLogger(__name__)
User = get_user_model()


class CreateOrderView(LoginRequiredMixin, View):
    """Создание заказа и попытка оплаты"""

    def post(self, request, model_name, product_id):
        form = PurchaseForm(request.POST)

        if not form.is_valid():
            messages.error(request, "Некорректные данные!")
            return redirect("users:profile", pk=request.user.pk)
        logger.info(f"Данные формы: {form.cleaned_data}")
        # Получаем данные из формы
        amount = form.cleaned_data.get("amount", 1)
        price = form.cleaned_data["price"]
        player_id = form.cleaned_data["player_id"]
        payment_method = form.cleaned_data["payment_method"]
        logger.info(f"Обработано количество: {amount} шт. товара")
        try:
            logger.info("🔄 Начинаем транзакцию...")
            with transaction.atomic():  # Используем транзакцию для безопасности
                # Получаем товар
                logger.info(f"🔍 Начинаем обработку покупки: {amount} шт. товара (ID {product_id})")

                model = apps.get_model("products", model_name)
                if not model:
                    messages.error(request, "Некорректная категория товара!")
                    return JsonResponse({"success": False, "message": "Некорректные данные!"})

                try:
                    product = model.objects.select_for_update().get(
                        id=product_id
                    )  # Блокируем запись для других транзакций
                except model.DoesNotExist:
                    messages.error(request, "Товар не найден!")
                    return JsonResponse({"success": False, "message": "Товар не найден!"})
                logger.info(f"🔍 Проверяем, что товар с ID {product_id} существует и загружен корректно.")
                logger.info(f"✅ Найден товар: {product.title} (остаток: {getattr(product, 'quantity', 'Не указано')})")
                # 🔴 Проверка: достаточно ли товара на складе?
                has_quantity = hasattr(product, "quantity")
                logger.info(f"Проверка наличия поля 'quantity': {has_quantity}")
                if has_quantity:
                    if amount > product.quantity:
                        messages.error(request, "Недостаточное количество товара в наличии!")
                        return JsonResponse({"success": False, "message": "Недостаточное количество товара в наличии!"})
                    logger.info(
                        f"🔴 Уменьшаем количество товара на складе: {product.quantity} → {product.quantity - amount}"
                    )
                    # Уменьшаем количество товара
                    product.quantity -= amount
                    product.save()
                    logger.info(f"✅ Товар обновлён, остаток: {product.quantity}")
                else:
                    logger.info("💡 У товара нет поля 'quantity', покупка возможна только в одном экземпляре.")

                # Вычисляем финальную стоимость
                total_price = product.price * amount
                logger.info(f"💰 Общая сумма: {total_price} руб.")

                # 🔴 Создаём заказ
                order = Order.objects.create(
                    user=request.user,
                    seller=product.seller,
                    content_type=ContentType.objects.get_for_model(product),
                    object_id=product.id,
                    price=total_price,
                    description=product.description,
                    amount=amount,  # Сохраняем количество в заказе
                )
                logger.info(f"✅ Заказ создан: ID {order.id}, Количество: {order.amount}")
                logger.info(f"📦 Заказ создан: ID {order.id}, сумма {total_price} руб.")

                # ✅ Получаем или создаем чат, независимо от порядка buyer/seller

                user1, user2 = sorted([request.user, product.seller], key=lambda u: u.id)

                chat_room = ChatRoom.objects.filter(Q(buyer=user1, seller=user2) | Q(buyer=user2, seller=user1)).first()

                if not chat_room:
                    chat_room = ChatRoom.objects.create(buyer=user1, seller=user2)
                logger.info(f"📎 Используем чат-комнату: ID {chat_room.id}")

                # 🔽 Сообщение в чат
                message_text = (
                    f'✅ Покупатель <span class="username">{escape(request.user.username)}</span> создал <span class="order-id">заказ #{order.id}</span>.'
                    f"{escape(product.title)}, {amount} шт."
                    f'<span class="username">{escape(request.user.username)}</span>, не забудьте потом нажать кнопку '
                    f"«Подтвердить покупку»."
                )
                system_user = User.objects.get(username="LigaPay")
                ChatMessage.objects.create(
                    chat_room=chat_room,
                    sender=system_user,
                    message=message_text,
                )

                # ✅ Отправляем WebSocket-сообщение о создании заказа
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"chat_{chat_room.id}",
                    {
                        "type": "chat_message",
                        "message": message_text,
                        "sender": system_user.username,
                        "order_id": order.id,
                        "is_system": True,
                    },
                )
                # Потом сигнал клиенту отрисовать кнопку
                async_to_sync(channel_layer.group_send)(
                    f"chat_{chat_room.id}",
                    {
                        "type": "order_created",
                        "order_id": order.id,
                        "csrf_token": get_token(request),
                    },
                )
                logger.info(f"📤 WebSocket: отправлено событие order_created в chat_{chat_room.id}")

                messages.success(request, "Заказ создан! Подтвердите покупку в чате. ✅")
                logger.info(f"✅ Заказ создан без оплаты. ID заказа: {order.id}")
                return JsonResponse({"success": True, "message": "Заказ создан! Подтвердите покупку в чате."})

                # if order.process_payment():
                #     order.save()
                #     messages.success(request, f"Вы купили {amount} шт. товара! 🎉")
                #     logger.info("✅ Оплата прошла успешно. Баланс обновлён.")
                #     return JsonResponse({"success": True, "message": f"Вы купили {amount} шт. товара!"})
                # raise ValueError("Недостаточно средств!")

        except ValueError as e:
            logger.error(f"❌ Ошибка: {e}")
            return JsonResponse({"success": False, "message": str(e)})
        except Exception as e:
            logger.error(f"❌ Непредвиденная ошибка: {e}")
            return JsonResponse({"success": False, "message": "Произошла ошибка при оформлении заказа!"})


class ConfirmOrderView(View):
    """Подтверждение оплаты заказа"""

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.status != "pending":
            return JsonResponse({"success": False, "message": "Этот заказ уже подтвержден или отменен."})

        if not order.process_payment():
            return JsonResponse({"success": False, "message": "Ошибка оплаты! Недостаточно средств."})

        # Успешная оплата
        order.status = "paid"
        order.save()

        # Находим чат для этого заказа
        try:
            user1, user2 = sorted([request.user, order.seller], key=lambda u: u.id)

            chat_room = ChatRoom.objects.filter(Q(buyer=user1, seller=user2) | Q(buyer=user2, seller=user1)).first()
        except ChatRoom.DoesNotExist:
            return JsonResponse({"success": True, "message": "Покупка подтверждена, но чат не найден."})
        # 💾 Сохраняем сообщение в чат
        plain_message = (
            f'✅ <span class="username">{escape(request.user.username)}</span> оплатил '
            f'<span class="order-id">заказ #{order.id}</span> и отправил деньги продавцу '
            f'<span class="username">{escape(order.seller.username)}</span>.'
        )
        system_user = User.objects.get(username="LigaPay")

        ChatMessage.objects.create(
            chat_room=chat_room,
            sender=system_user,
            message=plain_message,
        )

        # WebSocket: отправляем событие
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{chat_room.id}",
            {
                "type": "chat_message",
                "sender": system_user.username,
                "message": plain_message,
                "order_id": order.id,
                "is_system": True,
            },
        )

        return JsonResponse({"success": True, "message": "Покупка подтверждена и оплачена!", "reload": True})


class OrderListView(LoginRequiredMixin, ContextMixin, ListView):
    """Вывод списка заказов пользователя"""

    model = Order
    template_name = "orders/order_list.html"
    context_object_name = "orders"
    title = "История покупок"

    def get_queryset(self):
        """Фильтруем заказы только для текущего пользователя"""
        return Order.objects.filter(user=self.request.user).order_by("-created_at")


class SaleListView(LoginRequiredMixin, ContextMixin, ListView):
    """Вывод списка продаж пользователя"""

    model = Order
    template_name = "orders/sale_list.html"
    context_object_name = "sales"
    title = "История продаж"

    def get_queryset(self):
        """Фильтруем заказы, где текущий пользователь является продавцом"""
        return Order.objects.filter(seller=self.request.user).order_by("-created_at")
