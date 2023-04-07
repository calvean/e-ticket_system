// Get menu elements
const menu = document.querySelector('.menu');
const menuBtn = document.querySelector('.menu-btn');
const closeBtn = document.querySelector('.close-btn');

// Toggle menu
menuBtn.addEventListener('click', () => {
  menu.classList.add('show-menu');
});

closeBtn.addEventListener('click', () => {
  menu.classList.remove('show-menu');
});

