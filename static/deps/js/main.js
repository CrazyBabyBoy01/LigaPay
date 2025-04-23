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
// Функция для закрытия текущего WebSocket
function closeSocket() {
    if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
        console.log('Закрытие старого соединения WebSocket...');
        chatSocket.close();  // Закрыть соединение
    }
}



const serviceTypeElement = document.querySelector("#service-type");
const serviceIdElement = document.querySelector("#service-id");

let chatSocket;
let roomName;


// Закрываем WebSocket перед открытием нового соединения
closeSocket();  // Закрываем старое соединение, если оно есть

// Проверяем, находимся ли мы в общем чате или в чате услуги
if (serviceTypeElement && serviceIdElement) {
    const serviceType = serviceTypeElement.dataset.type;
    const serviceId = serviceIdElement.dataset.id;
    roomName = `${serviceType}/${serviceId}`;
} else {
    roomName = "global_chat";  // Это общий чат
}

// Формируем URL для WebSocket
chatSocket = new WebSocket(`ws://127.0.0.1:8000/ws/chat/${roomName}/`);
// Подключаемся к WebSocket на текущем сайте (должен быть путь к чату)
// const chatSocket = new WebSocket('ws://127.0.0.1:8000/ws/chat/global_chat/');

// Обработка входящих сообщений
// chatSocket.onmessage = function(e) {
//     const data = JSON.parse(e.data);
//     document.querySelector('#chat-log').value += (data.message + '\n');  // Добавляем новое сообщение в чат
// };
chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);

    if (data.error) {
        // Если пришла ошибка (пользователь не авторизован), перенаправляем на страницу авторизации
        alert(data.error);
        window.location.href = "/users/autorization/";  // Перенаправляем на страницу авторизации
        return;
    }
    // Добавление нового сообщения в #chat-log
    const chatLog = document.querySelector('#chat-log');
    const messageElement = document.createElement('p');
    messageElement.innerHTML = `<strong>${data.sender}:</strong> ${data.message}`;
    chatLog.appendChild(messageElement);
    // Ограничиваем количество сообщений, например, до 10 последних
    const maxMessages = 4;
    const messages = chatLog.querySelectorAll('p');
    if (messages.length > maxMessages) {
        chatLog.removeChild(messages[0]);  // Удаляем старое сообщение
    }
    // Прокрутка вниз, чтобы показывать новые сообщения
    chatLog.scrollTop = chatLog.scrollHeight;
};
// Обработка закрытия соединения
chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

// Отправка сообщений по нажатию Enter
document.querySelector('#chat-message-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // Нажат Enter
        const messageInputDom = document.querySelector('#chat-message-input');
        const message = messageInputDom.value;
        chatSocket.send(JSON.stringify({'message': message}));  // Отправляем сообщение на сервер
        messageInputDom.value = '';  // Очищаем поле ввода
    }
};

console.log("JS загружен!");
