document.addEventListener('DOMContentLoaded', function() {
    if (localStorage.getItem('token') && localStorage.getItem('userId')) {
        window.location.href = 'sessions.html';
        return;
    }

    // Form containers
    const loginFormContainer = document.getElementById('loginFormContainer');
    const registerFormContainer = document.getElementById('registerFormContainer');

    // Toggle links
    const showRegister = document.getElementById('showRegister');
    const showLogin = document.getElementById('showLogin');

    // Popups
    const errorPopup = document.getElementById('errorPopup');
    const successPopup = document.getElementById('successPopup');

    // Function to toggle between Login and Register forms
    function toggleForms(showRegisterForm) {
        if (showRegisterForm) {
            loginFormContainer.style.display = 'none';
            registerFormContainer.style.display = 'block';
        } else {
            registerFormContainer.style.display = 'none';
            loginFormContainer.style.display = 'block';
        }
    }

    // Function to show error popup
    function showErrorPopup(message) {
        errorPopup.textContent = message;
        errorPopup.classList.add('show');
        setTimeout(() => {
            errorPopup.classList.remove('show');
        }, 3000); // Hide after 3 seconds
    }

    // Function to show success popup
    function showSuccess(message) {
        successPopup.textContent = message;
        successPopup.classList.add('show');
        setTimeout(() => {
            successPopup.classList.remove('show');
        }, 3000); // Hide after 3 seconds
    }

    // Event listeners for toggle links
    showRegister.addEventListener('click', function() {
        toggleForms(true);
    });

    showLogin.addEventListener('click', function() {
        toggleForms(false);
    });

    // Handle Login Form Submission
    const loginForm = document.getElementById('loginForm');
    loginForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission

        const email_id = document.getElementById('email_id').value.trim();
        const password = document.getElementById('password').value;

        // Basic validation
        if (!email_id || !password) {
            showErrorPopup('Please enter both email and password.');
            return;
        }

        fetch(`${backendUrl}/users/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "email": email_id,
                "pass": password
            })
        })
        .then(response => {
            if (response.status == 401) { 
                return response.json().then(data => {
                    throw new Error(data.description || 'Invalid credentials');
                });
            }
            if (response.status !== 200) { 
                return response.json().then(data => {
                    throw new Error(data.description || 'Unexpected error occurred.');
                });
            }
            return response.json(); 
        })
        .then(data => {
            // Assuming the response contains user_id and token
            localStorage.setItem('userId', data.user_id);
            localStorage.setItem('fullName', data.full_name);
            localStorage.setItem('token', data.token);
            
            document.getElementById('email_id').value = "";
            document.getElementById('password').value = "";
            window.location.href = 'sessions.html';

        })
        .catch(error => {
            console.error('Error while logging in user:', error);
            showErrorPopup(error.message);
            
        });
    });

    // Handle Register Form Submission
    const registerForm = document.getElementById('registerForm');
    registerForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the default form submission

        const fullName = document.getElementById('registerFullName').value.trim();
        const email_id = document.getElementById('registerEmail').value.trim();
        const password = document.getElementById('registerPassword').value;

        // Basic validation
        if (!fullName || !email_id || !password) {
            showErrorPopup('Please fill in all the fields.');
            return;
        }

        fetch(`${backendUrl}/users`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                "fullname": fullName,
                "email": email_id,
                "pass": password
            })
        })
        .then(response => {
            if (response.status !== 201) { 
                return response.json().then(data => {
                    throw new Error(data.description || 'Unexpected error occurred.');
                });
            }
            return response.json(); 
        })
        .then(data => {
            showSuccess('User created successfully');
            // Optionally, switch to login form after showing success
            setTimeout(() => {
                toggleForms(false);
            }, 1500); // Switch after 1.5 seconds
            document.getElementById('registerFullName').value = "";
            document.getElementById('registerEmail').value = "";
            document.getElementById('registerPassword').value = "";
        })
        .catch(error => {
            console.error('Error creating user:', error);
            showErrorPopup(error.message);
        });
    });

});