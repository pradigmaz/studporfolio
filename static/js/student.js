// project_create.html
// скрипт вызова формы url

document.addEventListener('DOMContentLoaded', function() {
  var categorySelect = document.querySelector('#category');
  var urlGroup = document.querySelector('#repository_url_group');
  categorySelect.addEventListener('change', function() {
    if (this.value === 'it') {
      urlGroup.style.display = 'block';
    } else {
      urlGroup.style.display = 'none';
    }
  });
});


// student_settings.html
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

// скрипт для сложности пароля
document.addEventListener("DOMContentLoaded", function () {
const passwordInput = document.querySelector('#new_password');
const strengthMeter = document.querySelector('#new_password_strength_meter');

if (passwordInput && strengthMeter) {
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


document.getElementById('searchForm').addEventListener('submit', function(event) {
event.preventDefault();
const form = event.target;
const formData = new FormData(form);
const params = new URLSearchParams(formData).toString();
fetch(`${form.action}?${params}`, {
    headers: {
        'X-Requested-With': 'XMLHttpRequest'
    }
})
.then(response => response.text())
.then(html => {
    document.getElementById('searchResults').innerHTML = html;
})
.catch(error => console.error('Error:', error));
});

document.addEventListener('DOMContentLoaded', function() {
var checkBox = document.getElementById("toggleSearch");
var searchInputGroup = document.getElementById("searchInputGroup");
var searchCategory = document.getElementById("searchCategory");
var specialtyGroup = document.getElementById("specialtyGroup");

checkBox.addEventListener('change', function() {
    if (checkBox.checked) {
        searchInputGroup.style.display = "block";
    } else {
        searchInputGroup.style.display = "none";
    }
});

searchCategory.addEventListener('change', function() {
    specialtyGroup.style.display = this.value === 'vacancies' ? 'block' : 'none';
});

// Initial check on page load
specialtyGroup.style.display = searchCategory.value === 'vacancies' ? 'block' : 'none';
});

function resetSpecialty() {
const category = document.getElementById('searchCategory').value;
if (category !== 'vacancies') {
    document.getElementById('specialty').selectedIndex = 0;
}
}
