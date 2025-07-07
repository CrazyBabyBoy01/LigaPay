// Получаем элементы
var modal = document.getElementById("modal");
var openModalBtn = document.getElementById("openModalBtn");
var closeModalBtn = document.getElementById("closeModalBtn");

// Получаем значение из скрытого элемента, который мы передали из шаблона
var authElement = document.getElementById("isAuthenticated");

if (authElement) {
    var isAuthenticated = authElement.value;
    console.log("Пользователь аутентифицирован:", isAuthenticated);
} else {
    console.warn("Элемент с id='isAuthenticated' не найден на этой странице.");
}






// // Открываем модальное окно для создания карточки при клике на кнопку
// var openModalBtn = document.getElementById("openModalBtn");

// if (openModalBtn) {  // Проверка, существует ли элемент
//     openModalBtn.onclick = function() {
//         console.log("Кнопка нажата");
//         console.log("isAuthenticated:", isAuthenticated);

//         if (isAuthenticated === "True") {
//             console.log("Пользователь авторизован");
//             modal.style.display = "flex";
//         } else {
//             console.log("Пользователь не авторизован");
//             window.location.href = "/users/autorization/"; // Убедитесь, что URL верный
//         }
//     };
// } else {
//     console.log("Кнопка не найдена на странице");
// }

function setupModal(openBtnId, modalId) {
    var openBtn = document.getElementById(openBtnId);
    var modal = document.getElementById(modalId);

    if (openBtn && modal) {
        openBtn.onclick = function () {
            if (isAuthenticated === "True") {
                modal.style.display = "flex";
            } else {
                window.location.href = "/users/autorization/";
            }
        };

        var closeBtn = modal.querySelector(".close");
        if (closeBtn) {
            closeBtn.onclick = function () {
                modal.style.display = "none";
            };
        }

        window.onclick = function (event) {
            if (event.target === modal) {
                modal.style.display = "none";
            }
        };
    } else {
        console.log("Не найдена кнопка или модалка: " + openBtnId + ", " + modalId);
    }
}

// Для создания
setupModal("openModalBtn", "modal");

// Для редактирования
setupModal("openEditModalBtn", "editModal");

// Закрытие модального окна
document.addEventListener("DOMContentLoaded", function() {
    var closeModalBtn = document.getElementById("closeModalBtn");
    var modal = document.getElementById("modal");

    if (closeModalBtn && modal) {
        // Закрываем модальное окно при клике на крестик
        closeModalBtn.onclick = function() {
            modal.style.display = "none";
        };

        // Закрываем модальное окно при клике вне области окна
        window.onclick = function(event) {
            if (event.target === modal) {
                modal.style.display = "none";
            }
        };
    } else {
        console.log("❌ Кнопка закрытия или модальное окно не найдены!");
    }
});



// Получаем элементы иконки и меню
const profileIcon = document.getElementById('profileIcon');
const dropdownMenu = document.getElementById('dropdownMenu');

// Добавляем событие на клик по иконке профиля
if (profileIcon && dropdownMenu) {
    profileIcon.addEventListener('click', function() {
        dropdownMenu.classList.toggle('show'); // Показать/скрыть меню
    });
}

// Закрытие меню при клике вне области меню
window.addEventListener('click', function(event) {
    // Проверяем, существуют ли profileIcon и dropdownMenu, прежде чем обращаться к ним
    if (profileIcon && dropdownMenu) {
        if (!profileIcon.contains(event.target) && !dropdownMenu.contains(event.target)) {
            dropdownMenu.classList.remove('show'); // Скрыть меню
        }
    }
});

var resetFiltersBtn = document.getElementById('resetFiltersBtn');
if (resetFiltersBtn) {
    resetFiltersBtn.addEventListener('click', function() {
        var url = this.getAttribute('data-url');
        window.location.href = url;  // Перенаправление на URL
    });
}


// Окошка всплывающиеся при покупке
// Проверяем, существует ли элемент с классом .details-form
const form = document.querySelector('.details-form');
if (form) {
    // Если элемент найден, добавляем обработчик события
    form.addEventListener('submit', function(event) {
        event.preventDefault();  // Предотвращаем стандартное поведение формы (перезагрузку страницы)

        const formData = new FormData(this);  // Собираем данные из формы

        // Отправляем данные на сервер с помощью Fetch API
        fetch(this.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value  // Указываем CSRF токен
            }
        })
        .then(response => response.json())  // Получаем ответ в формате JSON
        .then(data => {
            if (data.success) {
                showNotification('success', data.message);  // Успешное уведомление
            } else {
                showNotification('error', data.message);  // Ошибка
            }
        })
        .catch(error => {
            showNotification('error', 'Произошла ошибка, попробуйте позже.');
        });
    });
} else {
    console.log('Форма .details-form не найдена на странице.');
}

// Функция для отображения уведомлений
function showNotification(type, message) {
    const notification = document.createElement('div');
    notification.classList.add('notification', type);
    notification.textContent = message;
    const notificationsContainer = document.getElementById('notifications');
    notificationsContainer.appendChild(notification);  // Добавляем уведомление в контейнер

    // Добавляем класс для анимации появления
    setTimeout(function() {
        notification.classList.add('show');
    }, 100);  // Небольшая задержка для начала анимации

    // Убираем уведомление через 5 секунд
    setTimeout(function() {
        notification.classList.remove('show');  // Убираем анимацию
        // Удаляем уведомление из DOM после завершения анимации
        setTimeout(function() {
            notification.remove();
        }, 500);
    }, 5000);  // Уведомление исчезнет через 5 секунд
}

// === Загрузка изображения через AJAX ===
document.addEventListener("DOMContentLoaded", function() {
    const uploadImageBtn = document.getElementById("uploadImageBtn");
    const imageInput = document.getElementById("imageInput");
    const uploadImageForm = document.getElementById("uploadImageForm");

    if (uploadImageBtn && imageInput && uploadImageForm) {
        uploadImageBtn.addEventListener("click", () => {
            imageInput.click();
        });

        imageInput.addEventListener("change", () => {
            if (imageInput.files.length > 0) {
                const formData = new FormData();
                formData.append("add_image", "1");
                formData.append("image", imageInput.files[0]);

                console.log("Отправка файла:", imageInput.files[0]);  // <-- ПРОВЕРКА

                fetch(uploadImageForm.action, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                    },
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    console.log("Ответ от сервера:", data);  // <-- ПРОВЕРКА
                    if (data.success) {
                        showNotification("success", data.message);
                        setTimeout(() => location.reload(), 1000);
                    } else {
                        showNotification("error", data.message || "Ошибка при загрузке изображения.");
                    }
                })
                .catch((error) => {
                    console.error("Ошибка:", error);
                    showNotification("error", "Ошибка при отправке запроса.");
                });
            }
        });
    }
});

// === Удаление изображений через AJAX ===
document.addEventListener("DOMContentLoaded", function() {
    const deleteForms = document.querySelectorAll(".image-delete-form");

    deleteForms.forEach(form => {
        form.addEventListener("submit", function(event) {
            event.preventDefault();

            const formData = new FormData(form);
            fetch(form.action, {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification("success", data.message);
                    setTimeout(() => location.reload(), 1000);
                } else {
                    showNotification("error", data.message || "Ошибка при удалении.");
                }
            })
            .catch(error => {
                console.error("Ошибка:", error);
                showNotification("error", "Произошла ошибка при удалении.");
            });
        });
    });
});



document.addEventListener("DOMContentLoaded", function() {
    let amountInput = document.getElementById("amount");
    let priceInput = document.getElementById("price");
    let itemElement = document.getElementById("item-price");

    // Проверяем, найден ли элемент с id "item-price"
    let itemPrice = itemElement ? parseFloat(itemElement.getAttribute("data-price")) : 0;

    // Проверяем, найдены ли input'ы перед добавлением обработчика
    if (amountInput && priceInput) {
        amountInput.addEventListener("input", function() {
            let amount = parseInt(amountInput.value) || 0;
            priceInput.value = (amount * itemPrice).toFixed(2); // Умножаем на количество и округляем до 2 знаков

        });
    }
});

// // Добавляем изображение в карточку товара
// document.getElementById("uploadImageBtn").addEventListener("click", function() {
//     document.getElementById("imageInput").click(); // Открываем диалог выбора файла
// });

// document.getElementById("imageInput").addEventListener("change", function() {
//     if (this.files.length > 0) {
//         document.getElementById("uploadImageForm").submit(); // Автоотправка формы
//     }
// });

// Функция для закрытия текущего WebSocket
function closeSocket() {
    if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        console.log('Закрытие старого соединения WebSocket...');
        chatSocket.close();  // Закрыть соединение
    }
}


const chatIdElement = document.querySelector("#chat-id");
const serviceTypeElement = document.querySelector("#service-type");
const serviceIdElement = document.querySelector("#service-id");


let chatSocket;
let roomName;


// Закрываем WebSocket перед открытием нового соединения
closeSocket();  // Закрываем старое соединение, если оно есть

// Проверяем, находимся ли мы в общем чате или в чате услуги
if (chatIdElement &&
    chatIdElement.dataset.chatId) {
    // 🔹 Подключение по chat_id (диалог)
    const chatId = chatIdElement.dataset.chatId;
    roomName = `dialogs/${chatId}`;
} else if (serviceTypeElement && serviceIdElement) {
    // 🔹 Подключение по услуге
    const serviceType = serviceTypeElement.dataset.type;
    const serviceId = serviceIdElement.dataset.id;
    roomName = `${serviceType}/${serviceId}`;
} else {
    // 🔹 Общий чат
    roomName = "global_chat";
}


// Формируем URL для WebSocket
chatSocket = new WebSocket(`ws://127.0.0.1:8000/ws/chat/${roomName}/`);

document.addEventListener("DOMContentLoaded", function () {
    const chatLog = document.querySelector('#chat-log');
    const currentUser = document.querySelector("#current-user")?.dataset.username || "";

    if (chatLog) {
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    // Навешиваем обработчик на форму, если она уже есть
    setupConfirmHandler();

    // Обработка входящих сообщений
    chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);

        if (data.error) {
            alert(data.error);
            window.location.href = "/users/autorization/";
            return;
        }

        console.log("Received message:", data);

        // ✅ Новый заказ — показываем кнопку (если её ещё нет)
        if (data.type === "order_created") {
            const container = document.querySelector("#order-button-container");
            if (container && !document.getElementById("confirm-form")) {
                container.innerHTML = `
                    <form id="confirm-form" method="post" style="margin-top: 10px;">
                        <button type="submit" id="confirm-purchase-btn" class="header__btn" data-order-id="${data.order_id}">
                            Подтвердить покупку
                        </button>
                    </form>
                `;
                setupConfirmHandler();
            }
            return;
        }

        // ✅ Подтверждение заказа — убираем кнопку
        if (data.type === "order_confirmed") {
            const container = document.querySelector("#order-button-container");
            if (container) {
                container.innerHTML = "";
            }

            const messageElement = document.createElement('p');
            messageElement.innerHTML = `<strong>Система:</strong> ${data.message}`;
            chatLog.appendChild(messageElement);

            chatLog.scrollTop = chatLog.scrollHeight;
        }

        appendMessage({
            senderUsername: data.sender,
            messageText: data.message,
            timestamp: data.timestamp,
            currentUser: currentUser,
            chatLogElement: chatLog,
            isSystem: data.sender === "LigaPay"
        });

        const maxMessages = 50;
        const messages = chatLog.querySelectorAll('.message');
        if (messages.length > maxMessages) {
            chatLog.removeChild(messages[0]);
        }
    };

    chatSocket.onclose = function () {
        console.error('Chat socket closed unexpectedly');
    };

    // Отправка сообщений по Enter
    document.querySelector('#chat-message-input').onkeyup = function (e) {
        if (e.keyCode === 13) {
            const messageInputDom = document.querySelector('#chat-message-input');
            const message = messageInputDom.value;
            if (message.trim() !== "") {
                chatSocket.send(JSON.stringify({ 'message': message }));
                messageInputDom.value = '';
            }
        }
    };

    // ✅ Функция навешивания обработчика на форму подтверждения
    function setupConfirmHandler() {
        const confirmForm = document.getElementById("confirm-form");
        if (confirmForm) {
            confirmForm.addEventListener("submit", function (e) {
                e.preventDefault();
                const orderId = confirmForm.querySelector("#confirm-purchase-btn").dataset.orderId;

                fetch(`/orders/confirm/${orderId}/`, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCookie("csrftoken"),
                        "Content-Type": "application/json"
                    }
                })
                .then(res => res.json())
                .then(json => {
                    if (json.success) {
                        alert(json.message);
                        if (json.reload) {
                            location.reload();
                        }
                    } else {
                        alert("Ошибка: " + json.message);
                    }
                })
                .catch(err => {
                    console.error("Ошибка при подтверждении заказа:", err);
                });
            });
        }
    }
});



// Функция добавления сообщения в DOM
function appendMessage({ senderUsername, messageText, timestamp, currentUser, chatLogElement, isSystem}) {
    const date = timestamp ? new Date(timestamp) : new Date();
    const isoTimestamp = date.toISOString();
    const formattedDate = date.toLocaleString("ru-RU", {
        day: "2-digit",
        month: "2-digit",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit"
    });

    const messages = chatLogElement.querySelectorAll('.message');
    const lastMessageGroup = messages[messages.length - 1];

    const isCurrentUser = senderUsername === currentUser;

    let canAppend = false;
    if (lastMessageGroup && lastMessageGroup.classList.contains(isCurrentUser ? 'me' : 'them')) {
        const lastSender = lastMessageGroup.querySelector('.sender-name')?.textContent;
        const lastTimestampRaw = lastMessageGroup.dataset.timestamp;

        if (lastSender === senderUsername && lastTimestampRaw) {
            const lastTimestamp = new Date(lastTimestampRaw);
            const diffInMs = date - lastTimestamp;
            const diffInMinutes = diffInMs / (60 * 1000);

            if (diffInMinutes <= 1) {
                canAppend = true;
            }
        }
    }

    if (canAppend) {
        messageText.split('\n').forEach(line => {
            const textDiv = document.createElement("div");
            textDiv.classList.add("text");
            if (isSystem) {
                textDiv.innerHTML = line;
                textDiv.classList.add("system-message");  // добавляем класс
            } else {
                textDiv.textContent = line;
            }
            lastMessageGroup.appendChild(textDiv);
        });
    } else {
        const messageDiv = document.createElement("div");
        messageDiv.classList.add("message");
        if (isSystem) {
            messageDiv.classList.add("system-message");  // выделяем системные сообщения
        } else {
            messageDiv.classList.add(isCurrentUser ? "me" : "them");
        }
        messageDiv.dataset.timestamp = isoTimestamp; // 👈 сохраняем точное ISO-время

        const senderDiv = document.createElement("div");
        senderDiv.classList.add("sender");

        const senderName = document.createElement("strong");
        senderName.classList.add("sender-name");
        senderName.textContent = senderUsername;

        const timeSpan = document.createElement("span");
        timeSpan.classList.add("timestamp");
        timeSpan.textContent = formattedDate;

        senderDiv.appendChild(senderName);
        senderDiv.appendChild(timeSpan);
        messageDiv.appendChild(senderDiv);

        messageText.split('\n').forEach(line => {
            const textDiv = document.createElement("div");
            textDiv.classList.add("text");
            if (isSystem) {
                textDiv.innerHTML = line;
                textDiv.classList.add("system-message");
            } else {
                textDiv.textContent = line;
            }
            messageDiv.appendChild(textDiv);
        });

        chatLogElement.appendChild(messageDiv);
    }

    chatLogElement.scrollTop = chatLogElement.scrollHeight;
}


// Вспомогательная функцию для CSRF:
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function updateUnreadCount() {
    fetch('/chat/unread-count/')
        .then(response => response.json())
        .then(data => {
            const badge = document.querySelector('.profile-badge');
            if (data.unread_count > 0) {
                if (badge) {
                    badge.textContent = data.unread_count;
                } else {
                    const imgDiv = document.querySelector('.profile__img');
                    const span = document.createElement('span');
                    span.classList.add('profile-badge');
                    span.textContent = data.unread_count;
                    imgDiv.appendChild(span);
                }
            } else {
                if (badge) badge.remove();
            }
        });
}
console.log("JS загружен!");
