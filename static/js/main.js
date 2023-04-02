// This is the main JavaScript file for the Online Ticket System

// Code to toggle the menu
function toggleMenu() {
  const menu = document.querySelector('#menu');
  menu.classList.toggle('active');
}

// Code to show a success message
function showSuccessMessage(message) {
  const successMessage = document.querySelector('#success-message');
  successMessage.innerHTML = message;
  successMessage.classList.add('show');

  setTimeout(() => {
    successMessage.classList.remove('show');
  }, 3000);
}

// Code to show an error message
function showErrorMessage(message) {
  const errorMessage = document.querySelector('#error-message');
  errorMessage.innerHTML = message;
  errorMessage.classList.add('show');

  setTimeout(() => {
    errorMessage.classList.remove('show');
  }, 3000);
}

