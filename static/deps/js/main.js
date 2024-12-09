
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

// document.addEventListener('DOMContentLoaded', function () {
//     // Обработчик кликов по кнопкам категорий
//     document.querySelectorAll('.products-item').forEach(function(button) {
//         button.addEventListener('click', function () {
//             const categorySlug = button.getAttribute('data-slug'); // Получаем slug категории

//             // AJAX запрос для получения описания категории
//             fetch(`/category-description/${categorySlug}/`)
//                 .then(response => response.json())
//                 .then(data => {
//                     // Обновляем описание в div с id "category-description"
//                     document.getElementById('category-description').innerText = data.description;
//                 })
//                 .catch(error => console.error('Error fetching category description:', error));
//         });
//     });
// });


document.addEventListener('DOMContentLoaded', function () {
    const buttons = document.querySelectorAll('.products-item');

    buttons.forEach(function (button) {
        button.addEventListener('click', function () {
            const categorySlug = button.getAttribute('data-slug');
            const categoryTitle = button.getAttribute('data-title'); // Получаем название категории
            console.log('Клик по категории:', categorySlug);

            // Изменяем заголовок с добавлением "League of Legends"
            const titleElement = document.getElementById('category-title');
            if (titleElement) {
                titleElement.innerText = `${categoryTitle} League of Legends`; // Добавляем текст
            } else {
                console.error('Элемент #category-title не найден.');
            }

            // Получаем описание категории
            fetch(`/products/category-description/${categorySlug}/`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Ошибка сети');
                    }
                    return response.json();
                })
                .then(data => {
                    const descriptionElement = document.getElementById('category-description');
                    if (descriptionElement) {
                        descriptionElement.innerText = data.description; // Обновляем описание
                    } else {
                        console.error('Элемент #category-description не найден.');
                    }
                })
                .catch(error => console.error('Ошибка:', error));
        });
    });
});
