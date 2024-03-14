document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registration');
    const responseText = document.getElementById('response-text');
    const additionalDetailsSection = document.getElementById('additional-details-section');
    const selfDescriptionSection = document.getElementById('self-description-section');
    const popupModal = document.getElementById('popup-modal');
    const yesButton = document.getElementById('yes-button');
    const noButton = document.getElementById('no-button');

    // Initialize additional details section state on page load
    additionalDetailsSection.style.display = 'none';
    selfDescriptionSection.style.display = 'none';

    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the form from submitting normally

        // Get user details from the form
        const name = document.getElementById('name').value.trim();
        const age = document.getElementById('age').value.trim();
        const gender = document.getElementById('gender').value.trim();
        const contactNumber = document.getElementById('contact_number').value.trim();
        const county = document.getElementById('county').value.trim();
        const town = document.getElementById('town').value.trim();
        const education = document.getElementById('education').value.trim();
        const profession = document.getElementById('profession').value.trim();
        const maritalStatus = document.getElementById('marital_status').value.trim();
        const religion = document.getElementById('religion').value.trim();
        const ethnicity = document.getElementById('ethnicity').value.trim();
        const selfDescription = document.getElementById('self_description').value.trim();

        // Log the value of selfDescription
        console.log('Self Description:', selfDescription);

        // Construct SMS text string with appropriate prefixes based on registration steps
        let smsText = '';
        let route = ''; // Initialize the route variable

        // Step 1: Initial registration
        if (!education && !profession && !maritalStatus && !religion && !ethnicity && !selfDescription) {
            smsText = `start#${name}#${age}#${gender}#${county}#${town}#${contactNumber}`;
            route = 'http://localhost:8000/register'; // Set the route for initial registration
        }
        // Step 2: Additional details
        else if ((education || profession || maritalStatus || religion || ethnicity) && !selfDescription) {
            smsText = `details#${education}#${profession}#${maritalStatus}#${religion}#${ethnicity}`;
            route = 'http://localhost:8000/additional-details'; // Set the route for additional details
        }
      
        else if (selfDescription){
          if (selfDescription.startsWith("MYSELF")) {
            smsText = selfDescription;
        }  else{
              smsText = `MYSELF ${selfDescription}`;

            route = 'http://localhost:8000/final-registration'; 

        }
    }
        // Log the constructed SMS text and route
        console.log('SMS Text:', smsText);
        console.log('Route:', route);

        // Send SMS text to the backend
        fetch(route, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: smsText })
        })
        .then(response => response.json())
        .then(result => {
            // Handle backend response
            console.log('Response from server:', result);
            if (result && result.message) {
                // Display response message in the popup modal
                responseText.textContent = result.message;
                popupModal.style.display = 'block'; // Show the popup modal

                // Handle redirection or display of additional sections based on response
                if (result.message.includes('Would you like to provide additional details?')) {
                    // Show the additional details section
                    showAdditionalDetailsPopup();
                } else if (result.message.includes('This is the last stage of registration')) {
                    // Show the self-description section
                    selfDescriptionSection.style.display = 'block';
                    // Do not hide the additional details section
                    popupModal.style.display = 'none'; // Hide the popup modal
                } else if (result.message.includes('You are now registered for dating')) {
                    // Redirect to match page if registration is completed
                    window.location.href = 'http://localhost:8000/match';
                }
            } else {
                // Show a default message if no response message is received
                responseText.textContent = 'An error occurred during registration.';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            // Show an error message in the popup modal if an error occurs
            responseText.textContent = 'An error occurred during registration.';
            popupModal.style.display = 'block'; // Show the popup modal
        });
    });

    // Event listener for the "Yes" button
    yesButton.addEventListener('click', function() {
        // Hide the popup modal
        popupModal.style.display = 'none';
        // Display the additional details section
        additionalDetailsSection.style.display = 'block';
    });

    // Event listener for the "No" button
    noButton.addEventListener('click', function() {
        // Hide the popup modal
        popupModal.style.display = 'none';
        // Redirect the user to the match page
        window.location.href = 'http://localhost:8000/match';
    });

    // Function to show the additional details popup
    function showAdditionalDetailsPopup() {
        // Show the popup modal
        popupModal.style.display = 'block';
        // Set popup text
        responseText.textContent = 'Would you like to provide additional details?';
        // Do not hide the self-description section
        responseText.classList.add('additional-details-text');
    }
});
