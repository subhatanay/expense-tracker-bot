const backendUrl = "https://13.233.134.61"

function showErrorPopup(message) {
    errorPopup.textContent = message;
    errorPopup.classList.add('show');  // Add class to show popup

    // Automatically hide popup after 3 seconds
    setTimeout(() => {
        errorPopup.classList.remove('show');  // Remove class to hide popup
    }, 6000);
}

function showSuccess(message) {
    const successPopup = document.getElementById('successPopup');
    successPopup.textContent = message;
    successPopup.classList.add('show');
    // Hide after 3 seconds
    setTimeout(() => {
        successPopup.classList.remove('show');
    }, 3000);
}

