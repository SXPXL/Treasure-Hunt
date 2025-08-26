// JS separated from login.html
function validateLoginForm(event) {
  const teamNum = document.getElementById('team_num');
  const password = document.getElementById('password');
  let valid = true;
  if (!teamNum.value.trim()) {
    teamNum.style.borderColor = 'red';
    valid = false;
  } else {
    teamNum.style.borderColor = '';
  }
  if (!password.value.trim()) {
    password.style.borderColor = 'red';
    valid = false;
  } else {
    password.style.borderColor = '';
  }
  if (!valid) {
    event.preventDefault();
    alert('Please enter both Team No and Password.');
  }
}
document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('loginForm');
  if (form) {
    form.addEventListener('submit', validateLoginForm);
  }
});
