/**
 * Campus Complaint Portal — Frontend JavaScript
 */

// Toggle Password Visibility function for auth forms
function togglePasswordVisibility(inputId, btn) {
  const input = document.getElementById(inputId);
  if (!input) return;

  if (input.type === 'password') {
    input.type = 'text';
    btn.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
        <line x1="1" y1="1" x2="23" y2="23"></line>
      </svg>
    `;
    btn.title = "Hide password";
  } else {
    input.type = 'password';
    btn.innerHTML = `
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
        <circle cx="12" cy="12" r="3"></circle>
      </svg>
    `;
    btn.title = "Show password";
  }
}

// Auto dismiss flash alerts after 5 seconds if desired
document.addEventListener('DOMContentLoaded', () => {
  const flashAlerts = document.querySelectorAll('.flash-alert');
  flashAlerts.forEach(alert => {
    // Add close button if not present
    if (!alert.querySelector('.alert-close')) {
      const closeBtn = document.createElement('span');
      closeBtn.className = 'alert-close';
      closeBtn.innerHTML = '&times;';
      closeBtn.style.cursor = 'pointer';
      closeBtn.style.marginLeft = '12px';
      closeBtn.style.fontWeight = 'bold';
      closeBtn.onclick = () => alert.remove();
      alert.appendChild(closeBtn);
    }
  });
});
