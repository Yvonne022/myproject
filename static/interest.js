document.addEventListener('DOMContentLoaded', function() {

  // Event listener for form submission
  document.getElementById('expressInterestForm').addEventListener('submit', handleSubmit);

  async function handleSubmit(event) {

    event.preventDefault();

    const requestedPerson = document.getElementById('requestedPersonName').value;  
    const requester = document.getElementById('requesterName').value;

    try {
      
      // Make fetch request  
      const response = await fetch('/express-interest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          text: `${requestedPerson},${requester}`
        })
      });

      // Log response
      console.log('Fetch response:', response);

      // Parse response body  
      const data = await response.json();

      // Log parsed data  
      console.log('Parsed data:', data);

      // Handle success response
      alert(data.message);

      // If the message indicates that the user should send "YES" to get more details
      if (data.message.includes('Send YES to')) {
        const userInput = prompt("Please enter 'YES' if you want to know more about them:");
        if (userInput && userInput.trim().toUpperCase() === 'YES') {
          // Make another fetch request to retrieve the requester's details
          const requesterDetailsResponse = await fetch('/express-interest', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            },
            body: JSON.stringify({
              text: 'YES',
              requester_name: requester
            })
          });

          // Parse the response to get the requester's details
          const requesterDetailsData = await requesterDetailsResponse.json();
          const wantDescription = confirm(requesterDetailsData.message); // Display the requester's details and confirm if user wants description
          if (wantDescription) {
            const descriptionInput = prompt("Please enter 'DESCRIBE' followed by the phone number:");
            if (descriptionInput && descriptionInput.trim().toUpperCase().startsWith('DESCRIBE')) {
              // Extract phone number from input
              const phoneNumber = descriptionInput.trim().split(' ')[1];
              // Make fetch request to get description
              const descriptionResponse = await fetch('/describe', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'Accept': 'application/json'
                },
                body: JSON.stringify({
                  text: `DESCRIBE ${phoneNumber}`
                })
              });
              // Parse the response to get the description
              const descriptionData = await descriptionResponse.json();
              if (descriptionData.description) {
                alert(descriptionData.description); // Display the description
              } else {
                alert(`${requester} has not provided a self-description.`);
              }
            } else {
              alert("Invalid input. Please follow the format: 'DESCRIBE phone_number'.");
            }
          }
        }
      }

    } catch (err) {

      // Catch errors
      console.error('Error:', err);
      alert('An error occurred. Please check console for details.');

    }

  }

});
