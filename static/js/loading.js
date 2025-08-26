
// Helper to initialize Lottie animation if not already initialized

function ensureLottieAnimation(retryCount = 0) {
  var box = document.getElementById('lottie-global-box');
  if (window.lottie && box) {
    if (!box.hasChildNodes()) {
      window.lottie.loadAnimation({
        container: box,
        renderer: 'svg',
        loop: true,
        autoplay: true,
        path: '/UI/Treasure box.json'
      });
    }
  } else if (retryCount < 10) {
    // Retry every 100ms up to 1s
    setTimeout(function() { ensureLottieAnimation(retryCount + 1); }, 100);
  }
}

// Load Lottie library if not present
if (!window.lottie) {
  var script = document.createElement('script');
  script.src = 'https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.10.2/lottie.min.js';
  script.onload = ensureLottieAnimation;
  document.head.appendChild(script);
} else {
  ensureLottieAnimation();
}

// Try to initialize Lottie as soon as possible
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', ensureLottieAnimation);
} else {
  ensureLottieAnimation();
}

// Also observe DOM changes in case overlay is injected late
const observer = new MutationObserver(ensureLottieAnimation);
observer.observe(document.body, { childList: true, subtree: true });

function showLoadingOverlay() {
  var overlay = document.getElementById('global-loading-overlay');
  if (overlay) {
    overlay.style.display = 'flex';
    ensureLottieAnimation();
  }
}

function hideLoadingOverlay() {
  // Remove all overlays with this id (in case of duplicates)
  var overlays = document.querySelectorAll('#global-loading-overlay');
  overlays.forEach(function(overlay) {
    overlay.remove();
  });
}

// Intercept all link clicks and form submissions to show loading overlay for at least 1 second before navigation
function interceptNavigation() {
  // Intercept anchor tag clicks
  document.querySelectorAll('a[href]').forEach(function(link) {
    link.addEventListener('click', function(e) {
      // Only intercept left-clicks and non-target _blank
      if (e.button === 0 && (!link.target || link.target === '_self')) {
        e.preventDefault();
        showLoadingOverlay();
        setTimeout(function() {
          window.location.href = link.href;
        }, 1000);
      }
    });
  });
  // Intercept form submissions
  document.querySelectorAll('form').forEach(function(form) {
    form.addEventListener('submit', function(e) {
      // Only intercept if not already handled
      if (!form.dataset.loadingIntercepted) {
        e.preventDefault();
        form.dataset.loadingIntercepted = 'true';
        showLoadingOverlay();
        setTimeout(function() {
          form.submit();
        }, 1000);
      }
    });
  });
}


document.addEventListener('DOMContentLoaded', interceptNavigation);

// Hide loading overlay when the page is fully loaded
window.addEventListener('load', function() {
  setTimeout(hideLoadingOverlay, 300); // slight delay for smoothness
});
