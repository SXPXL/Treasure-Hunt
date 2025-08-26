document.getElementById('excelUploadForm').addEventListener('submit', function(e) {
  var fileInput = document.getElementById('excelFile');
  if (!fileInput.value.match(/\.(xlsx|xls)$/i)) {
    alert('Please select a valid Excel file (.xlsx or .xls)');
    e.preventDefault();
  }
});
// Team search filter
function filterTeams() {
  var input = document.getElementById('teamSearchInput').value.trim().toLowerCase();
  var wrappers = document.querySelectorAll('.team-card-wrapper');
  wrappers.forEach(function(wrapper) {
    var teamNum = wrapper.getAttribute('data-team-num').toLowerCase();
    if (input === '' || teamNum.includes(input)) {
      wrapper.style.display = '';
    } else {
      wrapper.style.display = 'none';
    }
  });
}
function openDrawer() {
  document.getElementById('drawerMenu').classList.add('open');
  document.getElementById('drawerMenu').setAttribute('aria-hidden', 'false');
  document.getElementById('drawerMenu').focus();
  document.getElementById('drawerOverlay').classList.add('open');
  document.getElementById('hamburgerBtn').setAttribute('aria-expanded', 'true');
}
function closeDrawer() {
  document.getElementById('drawerMenu').classList.remove('open');
  document.getElementById('drawerMenu').setAttribute('aria-hidden', 'true');
  document.getElementById('drawerOverlay').classList.remove('open');
  document.getElementById('hamburgerBtn').setAttribute('aria-expanded', 'false');
}
