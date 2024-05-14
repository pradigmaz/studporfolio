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
// скрипт для формы телефона

document.addEventListener('DOMContentLoaded', function() {
  const phoneInputs = document.querySelectorAll('input[placeholder="+7 (___)-___-__-__"]');

  phoneInputs.forEach(input => {
    input.addEventListener('input', function(e) {
      let value = e.target.value.replace(/\D/g, '');
      if (value.length > 1) {
        value = `+7 (${value.substring(1, 4)}) ${value.substring(4, 7)}-${value.substring(7, 9)}-${value.substring(9, 11)}`;
      } else if (value.length === 1) {
        value = `+7 (${value}`;
      } else {
        value = '';
      }
      e.target.value = value;
    });

    input.addEventListener('keydown', function(e) {
      if (e.key === 'Backspace') {
        let value = e.target.value.replace(/\D/g, '');
        if (value.length === 1) {
          e.target.value = '';
        }
      }
    });

    input.addEventListener('focus', function(e) {
      if (e.target.value === '') {
        e.target.value = '+7 (';
      }
    });

    input.addEventListener('blur', function(e) {
      if (e.target.value === '+7 (') {
        e.target.value = '';
      }
    });
  });
});


// скрипт для показа пароля
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.toggle-password').forEach(item => {
        item.addEventListener('click', function () {
            const input = this.closest('.input-group').querySelector('.password-toggle');
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            this.classList.toggle('bi-eye');
            this.classList.toggle('bi-eye-slash');
        });
    });
});

// скрипт для проверки сложности пароля
