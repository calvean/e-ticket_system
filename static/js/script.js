const signupForm = document.getElementById("signup-form");
const signinForm = document.getElementById("signin-form");
const adminForm = document.getElementById("admin-form");

const signupBtn = document.getElementById("signupBtn");
const signinBtn = document.getElementById("signinBtn");
const adminBtn = document.getElementById("adminBtn");

const formTitle = document.getElementById("form-title");

// Hide all forms except the signup form
signinForm.style.display = "none";
adminForm.style.display = "none";

// Show the signup form by default
signupBtn.classList.add("active");

// Function to switch between forms
function switchForms(showForm, hideForm1, hideForm2, activeBtn, inactiveBtn1, inactiveBtn2, title) {
    showForm.style.display = "block";
    hideForm1.style.display = "none";
    hideForm2.style.display = "none";
    activeBtn.classList.add("active");
    inactiveBtn1.classList.remove("active");
    inactiveBtn2.classList.remove("active");
    formTitle.textContent = title;
}

// Event listeners for switching forms
signupBtn.addEventListener("click", function() {
    switchForms(signupForm, signinForm, adminForm, signupBtn, signinBtn, adminBtn, "Sign Up");
});

signinBtn.addEventListener("click", function() {
    switchForms(signinForm, signupForm, adminForm, signinBtn, signupBtn, adminBtn, "Sign In");
});

adminBtn.addEventListener("click", function() {
    switchForms(adminForm, signupForm, signinForm, adminBtn, signupBtn, signinBtn, "Admin Login");
});

