/* SnapVault — Main JavaScript
   Lightweight enhancements that complement Bootstrap 5.
   No external JS libraries required. */


// ── Auto-dismiss flash messages after 5 seconds ─────────────────────────
document.addEventListener('DOMContentLoaded', function () {

    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            // Use Bootstrap's built-in fade-out if available
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

});


// ── File upload: show selected filename in the form ─────────────────────
document.addEventListener('DOMContentLoaded', function () {

    const fileInput = document.getElementById('file-input');
    if (fileInput) {
        fileInput.addEventListener('change', function () {
            const fileName = this.files[0] ? this.files[0].name : '';
            const label = document.querySelector('label[for="file-input"]');
            if (label && fileName) {
                label.textContent = fileName;
            }
        });
    }

});


// ── Search input: submit on Enter key ───────────────────────────────────
document.addEventListener('DOMContentLoaded', function () {

    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                document.getElementById('search-form').submit();
            }
        });
    }

});