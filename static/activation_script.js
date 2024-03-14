document.addEventListener('DOMContentLoaded', function() {
    const activationForm = document.getElementById('activationForm');
    const responseDiv = document.getElementById('response');

    activationForm.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the form from submitting normally
        
        // Get the activation keyword entered by the user
        const activationKeyword = document.getElementById('activationKeyword').value;

        // Make AJAX POST request to the backend
        fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: activationKeyword }) // Sending the activation keyword to the backend
        })
        .then(response => response.json())
        .then(result => {
            // Handle backend response
            responseDiv.textContent = result.message;
            
            // Check if the response indicates successful activation
            if (result.message.includes('Welcome to our dating service')) {
                // Redirect to the registration page
                window.location.href = '/';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            responseDiv.textContent = 'An error occurred. Please try again later.';
        });
    });
});
