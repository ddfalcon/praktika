// Мобильное меню
const burger = document.getElementById('burger');
const nav = document.getElementById('nav');
if (burger) {
    burger.addEventListener('click', () => nav.classList.toggle('nav--open'));
}
// Шапка с тенью при прокрутке
const header = document.querySelector('.header');
window.addEventListener('scroll', () => {
    header.classList.toggle('header--scrolled', window.scrollY > 10);
});
// Автоскрытие уведомлений
setTimeout(() => {
    document.querySelectorAll('.alert').forEach(a => {
        a.style.transition = 'opacity .4s';
        a.style.opacity = '0';
        setTimeout(() => a.remove(), 400);
    });
}, 3500);
