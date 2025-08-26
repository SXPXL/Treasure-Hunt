// JS separated from gallery.html
function openMediaModal(url, type) {
  var modal = document.getElementById('mediaModal');
  var content = document.getElementById('modalContent');
  if(type === 'video') {
    content.innerHTML = '<video src="' + url + '" controls autoplay style="max-width:96vw; max-height:90vh; border-radius:16px; background:#222;"></video>';
  } else {
    content.innerHTML = '<img src="' + url + '" style="max-width:96vw; max-height:90vh; border-radius:16px; background:#222;">';
  }
  modal.style.display = 'flex';
  document.body.style.overflow = 'hidden';
}
function closeMediaModal() {
  document.getElementById('mediaModal').style.display = 'none';
  document.getElementById('modalContent').innerHTML = '';
  document.body.style.overflow = '';
}
document.addEventListener('keydown', function(e) {
  if(e.key === 'Escape') closeMediaModal();
});
