
    document.addEventListener('DOMContentLoaded', function () {
        // Get the form fields
        const usernameField = document.getElementById('id_username');
        const emailField = document.getElementById('id_email');
        const password1Field = document.getElementById('id_password1');
        const password2Field = document.getElementById('id_password2');

        // Get the error message containers
        const usernameError = document.getElementById('username-error');
        const emailError = document.getElementById('email-error');
        const password1Error = document.getElementById('password1-error');
        const password2Error = document.getElementById('password2-error');

        // Maximum username length
        const MAX_USERNAME_LENGTH = 150;

        // Add event listeners for real-time validation
        usernameField.addEventListener('input', function () {
            if (usernameField.value.length > MAX_USERNAME_LENGTH) {
                usernameError.textContent = `Username cannot exceed ${MAX_USERNAME_LENGTH} characters.`;
                usernameError.style.display = 'block';
            } else {
                usernameError.style.display = 'none';
            }
        });

        emailField.addEventListener('input', function () {
            const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
            if (!emailPattern.test(emailField.value)) {
                emailError.textContent = 'Please enter a valid email address.';
                emailError.style.display = 'block';
            } else {
                emailError.style.display = 'none';
            }
        });

        password1Field.addEventListener('input', function () {
            if (password1Field.value.length < 8) {
                password1Error.textContent = 'Password must be at least 8 characters long.';
                password1Error.style.display = 'block';
            } else {
                password1Error.style.display = 'none';
            }
        });

        password2Field.addEventListener('input', function () {
            if (password1Field.value !== password2Field.value) {
                password2Error.textContent = 'Passwords do not match.';
                password2Error.style.display = 'block';
            } else {
                password2Error.style.display = 'none';
            }
        });
    });