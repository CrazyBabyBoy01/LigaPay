



// document.addEventListener('DOMContentLoaded', function () {
//     const buttons = document.querySelectorAll('.products-item');

//     buttons.forEach(function (button) {
//         button.addEventListener('click', function () {
//             const categorySlug = button.getAttribute('data-slug');
//             const categoryTitle = button.getAttribute('data-title'); // Получаем название категории
//             console.log('Клик по категории:', categorySlug);

//             // Изменяем заголовок с добавлением "League of Legends"
//             const titleElement = document.getElementById('category-title');
//             if (titleElement) {
//                 titleElement.innerText = `${categoryTitle} League of Legends`; // Добавляем текст
//             } else {
//                 console.error('Элемент #category-title не найден.');
//             }

//             // Получаем описание категории
//             fetch(`/products/category-description/${categorySlug}/`)
//                 .then(response => {
//                     if (!response.ok) {
//                         throw new Error('Ошибка сети');
//                     }
//                     return response.json();
//                 })
//                 .then(data => {
//                     const descriptionElement = document.getElementById('category-description');
//                     if (descriptionElement) {
//                         descriptionElement.innerText = data.description; // Обновляем описание
//                     } else {
//                         console.error('Элемент #category-description не найден.');
//                     }
//                 })
//                 .catch(error => console.error('Ошибка:', error));

//                 // Получаем контент категории (товары, фильтры и т.д.)
//             fetch(`/products/products/${categorySlug}/`)
//                 .then(response => {
//                     if (!response.ok) {
//                         throw new Error('Ошибка сети при получении контента');
//                     }
//                     return response.json();
//                 })
//                 .then(data => {
//                     const contentElement = document.getElementById('products-content');
//                     if (contentElement) {
//                         contentElement.innerHTML = data.content; // Обновляем содержимое
//                     }
//                 })
//                 .catch(error => console.error('Ошибка:', error));

//             // Обновляем URL в адресной строке
//             const newUrl = `/products/products/${categorySlug}/`;  // Новый URL с slug категории
//             window.history.pushState({ path: newUrl }, '', newUrl);

//         });
//     });
// });

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
