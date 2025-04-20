// Оборачиваю весь код в DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
  // project_create.html
  // скрипт вызова формы url
  var categorySelect = document.querySelector('#category');
  var urlGroup = document.querySelector('#repository_url_group');

  if (categorySelect && urlGroup) {
    categorySelect.addEventListener('change', function() {
      if (this.value === 'it') {
        urlGroup.style.display = 'block';
      } else {
        urlGroup.style.display = 'none';
      }
    });
    urlGroup.style.display = categorySelect.value === 'it' ? 'block' : 'none';
  }

  // student_settings.html
  // скрипт для валидации и форматирования ввода номера телефона
  const phoneInputs = document.querySelectorAll('input[name="phone"]');

  phoneInputs.forEach(function(input) {
    input.addEventListener('input', function(e) {
      let x = e.target.value.replace(/\D/g, '').match(/(\d{1})(\d{0,3})(\d{0,3})(\d{0,2})(\d{0,2})/);
      if (!x) return;
      e.target.value = '+7 ' + (x[2] ? '(' + x[2] : '') + (x[3] ? ') ' + x[3] : '') + (x[4] ? '-' + x[4] : '') + (x[5] ? '-' + x[5] : '');
    });
  });

  // скрипт для скрытия и показа пароля
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

  var searchForm = document.getElementById('searchForm');
  if (searchForm) {
    searchForm.addEventListener('submit', function(event) {
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
          const searchResults = document.getElementById('searchResults');
          if (searchResults) {
              searchResults.innerHTML = html;
          }
      })
      .catch(error => console.error('Error:', error));
    });
  }

  var checkBox = document.getElementById("toggleSearch");
  var searchInputGroup = document.getElementById("searchInputGroup");
  var searchCategory = document.getElementById("searchCategory");
  var specialtyGroup = document.getElementById("specialtyGroup");

  if (checkBox && searchInputGroup) {
    checkBox.addEventListener('change', function() {
        if (checkBox.checked) {
            searchInputGroup.style.display = "block";
        } else {
            searchInputGroup.style.display = "none";
        }
    });
  }

  if (searchCategory && specialtyGroup) {
    searchCategory.addEventListener('change', function() {
        specialtyGroup.style.display = this.value === 'vacancies' ? 'block' : 'none';
    });

    // Initial check on page load
    specialtyGroup.style.display = searchCategory.value === 'vacancies' ? 'block' : 'none';
  }

  // Эта функция должна быть доступна глобально, поэтому выносим ее за пределы DOMContentLoaded
});

// Делаем функцию resetSpecialty глобальной
function resetSpecialty() {
  const category = document.getElementById('searchCategory');
  const specialty = document.getElementById('specialty');
  
  if (category && specialty && category.value !== 'vacancies') {
    specialty.selectedIndex = 0;
  }
}
