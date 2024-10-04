
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
