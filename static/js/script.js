// script.js
// ----------
// Small extra behaviours for the site.

document.addEventListener('DOMContentLoaded', function () {
    // Automatically hide flash messages (the green/red alert boxes) after 4 seconds.
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alertEl) {
        setTimeout(function () {
            if (window.bootstrap) {
                const bsAlert = window.bootstrap.Alert.getOrCreateInstance(alertEl);
                bsAlert.close();
            }
        }, 4000);
    });
});
