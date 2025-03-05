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

// Открываем модальное окно при клике на кнопку
var openModalBtn = document.getElementById("openModalBtn");

if (openModalBtn) {  // Проверка, существует ли элемент
    openModalBtn.onclick = function() {
        console.log("Кнопка нажата");
        console.log("isAuthenticated:", isAuthenticated);

        if (isAuthenticated === "True") {
            console.log("Пользователь авторизован");
            modal.style.display = "flex";
        } else {
            console.log("Пользователь не авторизован");
            window.location.href = "/users/autorization/"; // Убедитесь, что URL верный
        }
    };
} else {
    console.log("Кнопка не найдена на странице");
}


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
profileIcon.addEventListener('click', function() {
    dropdownMenu.classList.toggle('show'); // Показать/скрыть меню
});

// Закрытие меню при клике вне области меню
window.addEventListener('click', function(event) {
    if (!profileIcon.contains(event.target) && !dropdownMenu.contains(event.target)) {
        dropdownMenu.classList.remove('show'); // Скрыть меню
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

console.log("JS загружен!");
