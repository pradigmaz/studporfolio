document.addEventListener("DOMContentLoaded", function () {
  CKEDITOR.replace("responsibilities");
  CKEDITOR.replace("requirements");
  CKEDITOR.replace("conditions");
  CKEDITOR.replace("key_skills");
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