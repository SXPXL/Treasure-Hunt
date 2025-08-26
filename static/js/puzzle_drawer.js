// JS for puzzle.html to enable the drawer menu, same as home.js
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
