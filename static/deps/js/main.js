// Получаем элементы
var modal = document.getElementById("modal");
var openModalBtn = document.getElementById("openModalBtn");
var closeModalBtn = document.getElementById("closeModalBtn");

// Получаем значение из скрытого элемента, который мы передали из шаблона
var isAuthenticated = document.getElementById("isAuthenticated").value;

// Открываем модальное окно при клике на кнопку
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


// Закрываем модальное окно при клике на крестик
closeModalBtn.onclick = function() {
    modal.style.display = "none";
}

// Закрываем модальное окно при клике вне области окна
window.onclick = function(event) {
    if (event.target == modal) {
        modal.style.display = "none";
    }
}

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

document.getElementById('resetFiltersBtn').addEventListener('click', function() {
    var url = this.getAttribute('data-url');
    window.location.href = url;  // Перенаправление на URL
});
