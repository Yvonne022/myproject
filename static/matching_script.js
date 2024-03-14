document.addEventListener('DOMContentLoaded', function() {
    // Element selections
    const matchingForm = document.getElementById('matching'); 
    const matchResponse = document.getElementById('match-response');
    const userDetailsContainer = document.getElementById('userDetailsContainer');
    const userDetailsModal = document.getElementById('userDetailsModal');
    const modalCloseBtn = document.querySelector('.close');

    // Get the user ID from the server-side rendered HTML
    const userId = matchingForm.getAttribute('data-user-id');

    // Add submit handler  
    matchingForm.addEventListener('submit', function(event) {
        event.preventDefault();

        // Get values from form inputs
        const ageRange = document.getElementById('ageRange').value.trim();
        const town = document.getElementById('town').value.trim();

        // Fetch matching users
        fetch('/match', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: `match#${ageRange}#${town}`, user_id: userId }) // Include the user ID
        })
        .then(response => response.json())
        .then(result => {
            // Handle response
            matchResponse.innerHTML = '';
            if (result.message) {
                matchResponse.innerHTML = result.message;
                // Add event listeners to the dynamically created <a> tags
                const userDetailsLinks = document.querySelectorAll('.user-details');
                userDetailsLinks.forEach(link => {
                    link.addEventListener('click', function(event) {
                        // Handle click event
                        event.preventDefault();
                        const phoneNumber = this.dataset.phoneNumber;
                        // Fetch user details
                        fetch('/user-details', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ text: phoneNumber })
                        })
                        .then(response => response.json())
                        .then(result => {
                            // Handle user details response
                            if (result.details) {
                                // Display user details
                                userDetailsContainer.innerHTML = result.details;
                                userDetailsModal.style.display = 'block';
                                // Fetch self-description
                                fetch('/describe', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json'
                                    },
                                    body: JSON.stringify({ text: `DESCRIBE ${phoneNumber}` }) 
                                })
                                .then(response => response.json())
                                .then(descriptionResult => {
                                    // Handle self-description response
                                    if (descriptionResult.description) {
                                        // Display self-description
                                        userDetailsContainer.innerHTML += `<p><strong>Self Description:</strong> ${descriptionResult.description}</p>`;
                                    } else {
                                        // Display fallback message
                                        userDetailsContainer.innerHTML += `<p>No Self Description has been provided.</p>`;
                                    }
                                    // Add Express Interest button
                                    userDetailsContainer.innerHTML += `<button class="express-interest" data-requested-person-name="${result.name}" data-requester-name="${result.name}">Express Interest</button>`;
                                    // Add event listener for the Express Interest button
                                    const expressInterestBtns = document.querySelectorAll('.express-interest');
                                    expressInterestBtns.forEach(btn => {
                                        btn.addEventListener('click', function() {
                                            // Handle Express Interest button click
                                            window.location.href = '/express-interest';  
                                            document.getElementById('requestedPersonName').value = result.name;
                                            document.getElementById('requesterName').value = result.name;  
                                            document.getElementById('expressInterestForm').style.display = 'block';
                                        });
                                    });
                                })
                                .catch(error => {
                                    console.error('Error:', error);
                                });
                            } else {
                                // Display fallback message for users with no additional details
                                userDetailsContainer.innerHTML = `<p><strong>No additional details have been provided.</strong></p>`;
                                // Add Express Interest button
                                userDetailsContainer.innerHTML += `<button class="express-interest" data-requested-person-name="${result.name}" data-requester-name="${result.name}">Express Interest</button>`;
                                // Add event listener for the Express Interest button
                                const expressInterestBtns = document.querySelectorAll('.express-interest');
                                expressInterestBtns.forEach(btn => {
                                    btn.addEventListener('click', function() {
                                        // Handle Express Interest button click
                                        window.location.href = '/express-interest';  
                                        document.getElementById('requestedPersonName').value = result.name;
                                        document.getElementById('requesterName').value = result.name;  
                                        document.getElementById('expressInterestForm').style.display = 'block';
                                    });
                                });
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            alert('An error occurred while fetching user details.');
                        });
                    });
                });
            } else {
                matchResponse.innerHTML = "<p>No matching users found.</p>";
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while fetching matching users.');
        });
    });

    // Add event listener for modal close button
    modalCloseBtn.addEventListener('click', function() {
        userDetailsModal.style.display = 'none';
    });

    // Add event listener for window click
    window.addEventListener('click', function(event) {
        if (event.target === userDetailsModal) {
            userDetailsModal.style.display = 'none';
        }
    });
});
