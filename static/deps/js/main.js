$('.header__burger').click(function (e) {
    e.preventDefault();
    $('ul.header__list').toggleClass('show');
})

$('ul.header__list li a').click(function (e) {
    e.preventDefault();
    $('ul.header__list').toggleClass('show');
})
