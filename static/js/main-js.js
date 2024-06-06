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

// скрит для сложности пароля
document.addEventListener("DOMContentLoaded", function () {
  const modals = ['#registerModalStudent', '#registerModalEmployer'];
  modals.forEach(modal => {
    const passwordInput = document.querySelector(`${modal} input[name="password"]`);
    if (passwordInput) {
      const strengthMeter = document.createElement("div");
      strengthMeter.classList.add("strengthMeter");
      passwordInput.parentNode.appendChild(strengthMeter);

      passwordInput.addEventListener("input", function () {
        const value = passwordInput.value;
        let strength = 0;
        if (/[A-Z]/.test(value)) strength++;
        if (/[a-z]/.test(value)) strength++;
        if (/[0-9]/.test(value)) strength++;
        if (/[\W]/.test(value)) strength++;
        if (value.length >= 8) strength++;

        strengthMeter.style.width = `${strength * 20}%`;
        strengthMeter.style.backgroundColor =
          strength < 3 ? "red" : strength < 4 ? "yellow" : "green";
      });
    }
  });
});

// скрипт для скрытия и показа пароля
document.addEventListener("DOMContentLoaded", function () {
  const togglePasswordButtons = document.querySelectorAll(".toggle-password");
  togglePasswordButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const passwordInputId = this.getAttribute("data-target");
      const passwordInput = document.getElementById(passwordInputId);
      const icon = this.querySelector("i");

      if (passwordInput.type === "password") {
        passwordInput.type = "text";
        icon.classList.remove("bi-eye");
        icon.classList.add("bi-eye-slash");
      } else {
        passwordInput.type = "password";
        icon.classList.remove("bi-eye-slash");
        icon.classList.add("bi-eye");
      }
    });
  });
});

// скрипт для валидации форм
$(document).ready(function() {
  $('#loginForm').on('submit', function(event) {
    event.preventDefault();
    var form = $(this);
    if (form.parsley().isValid()) {
      $.ajax({
        type: 'POST',
        url: form.attr('action'),
        data: form.serialize(),
        success: function(response) {
          if ($(response).find('#error-message').length) {
            $('#error-message').show();
          } else {
            window.location.href = response;
          }
        }
      });
    }
  });
});