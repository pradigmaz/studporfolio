// main.html
// Скрипт для анимации навбара

document.addEventListener("DOMContentLoaded", function(){
  const navbar = document.querySelector('.navbar');
  window.onscroll = function() {
    if (window.pageYOffset > 100) {
      navbar.classList.add('navbar-shrink');
    } else {
      navbar.classList.remove('navbar-shrink');
    }
  };
});

// base_index.html
// скрипт для валидации и форматирования ввода номера телефона
document.addEventListener('DOMContentLoaded', function() {
  const phoneInputs = document.querySelectorAll('input[name="phone"]');
  
  phoneInputs.forEach(function(input) {
    input.addEventListener('input', function(e) {
      let x = e.target.value.replace(/\D/g, '').match(/(\d{1})(\d{0,3})(\d{0,3})(\d{0,2})(\d{0,2})/);
      if (!x) return;
      e.target.value = '+7 ' + (x[2] ? '(' + x[2] : '') + (x[3] ? ') ' + x[3] : '') + (x[4] ? '-' + x[4] : '') + (x[5] ? '-' + x[5] : '');
    });
  });
});


// скрипт для показа пароля
document.addEventListener('DOMContentLoaded', function() {
  const togglePassword = document.querySelectorAll('.toggle-password');
  
  togglePassword.forEach(function(toggle) {
    toggle.addEventListener('click', function() {
      const passwordField = this.previousElementSibling;
      if (passwordField.type === 'password') {
        passwordField.type = 'text';
      } else {
        passwordField.type = 'password';
      }
    });
  });
});

// скрипт для сложности пароля
document.addEventListener('DOMContentLoaded', function() {
  const passwordFields = [
    { input: document.getElementById('password'), strength: document.getElementById('password-strength') },
    { input: document.getElementById('employer_password'), strength: document.getElementById('employer-password-strength') }
  ];

  passwordFields.forEach(field => {
    field.input.addEventListener('input', function() {
      const value = field.input.value;
      let strength = 0;
      if (value.length >= 8) strength++;
      if (/[A-Z]/.test(value)) strength++;
      if (/[a-z]/.test(value)) strength++;
      if (/[0-9]/.test(value)) strength++;
      if (/[\W_]/.test(value)) strength++;

      field.strength.style.width = '100%';
      field.strength.style.height = '5px';
      field.strength.style.borderRadius = '3px';
      field.strength.style.transition = 'background-color 0.5s, box-shadow 0.5s';

      if (strength <= 2) {
        field.strength.style.backgroundColor = 'red';
        field.strength.style.boxShadow = '0 0 10px red';
      } else if (strength <= 4) {
        field.strength.style.backgroundColor = 'yellow';
        field.strength.style.boxShadow = '0 0 10px yellow';
      } else {
        field.strength.style.backgroundColor = 'green';
        field.strength.style.boxShadow = '0 0 10px green';
      }
    });
  });

  document.querySelectorAll('.toggle-password').forEach(button => {
    button.addEventListener('click', function() {
      const input = this.previousElementSibling;
      input.type = input.type === 'password' ? 'text' : 'password';
    });
  });
});

// скрипт генерации пароля
function generatePassword(length = 12) {
  const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+";
  let password = "";
  for (let i = 0; i < length; i++) {
    const randomIndex = Math.floor(Math.random() * charset.length);
    password += charset[randomIndex];
  }
  return password;
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".generate-password").forEach((button) => {
    button.addEventListener("click", (event) => {
      const passwordField = event.target.previousElementSibling;
      passwordField.value = generatePassword();
    });
  });
});

// скрипт для модальных окон
document.addEventListener("hidden.bs.modal", function (event) {
  if (document.querySelectorAll(".modal.show").length) {
    document.body.classList.add("modal-open");
  } else {
    document.querySelectorAll(".modal-backdrop").forEach(function (backdrop) {
      backdrop.remove();
    });
  }
});
