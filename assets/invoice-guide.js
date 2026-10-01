/* Copy only the public template text. No client details, forms, or network calls. */
(() => {
  document.querySelectorAll('[data-copy-template]').forEach((button) => {
    const text = document.getElementById(button.dataset.copyTemplate);
    const status = document.getElementById(button.getAttribute('aria-describedby'));
    if (!text || !status || !navigator.clipboard?.writeText) return;
    button.hidden = false;
    button.addEventListener('click', async () => {
      button.disabled = true;
      status.textContent = '';
      try {
        await navigator.clipboard.writeText(text.textContent.trim());
        status.textContent = 'Copied. Replace every bracketed detail before sending.';
      } catch {
        status.textContent = 'Copy is unavailable in this browser. Select the email text and copy it manually.';
      } finally {
        button.disabled = false;
      }
    });
  });
})();
