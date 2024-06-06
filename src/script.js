document.getElementById('emailForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const email = document.getElementById('email').value;
    const subject = document.getElementById('subject').value;
    const loader = document.getElementById('loader');

    loader.style.display = 'block';

    console.log(window.location.hostname);
    // const baseUrl = window.location.hostname === "127.0.0.1" || 'localhost' ? 
    //             "http://localhost:3000" : 
    //             "https://educafic.com";
    // Using the new server endpoint to fetch student details and marks
    fetch(`http://localhost:3000/studentDetails?email=${email}&subject=${subject}`)
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP status ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Clear previous error message, if any
        loader.style.display = 'none';
        document.getElementById('error').textContent = '';

        if (data.userDetails && data.userDetails.length > 0) {
            const userDetails = data.userDetails[0];
            document.getElementById('userDetails').innerHTML = `
            <h2 style="color: #0FB995;">User Details</h2>
                <p><strong>Student Name:</strong> ${userDetails.student_name}</p>
                <p><strong>Student Email:</strong> ${userDetails.student_email}</p>
                <p><strong>Student Mobile Number:</strong> ${userDetails.student_mobile_number}</p>
            `;
        } else {
            document.getElementById('userDetails').innerHTML = '<p>No user details found.</p>';
        }

        // Check for user marks and display them
        if (data.message === 'No attempts') {
            document.getElementById('userMarks').innerHTML = '<p style="color: red;">No attempts</p>';
        } else if (data.userMarks && data.userMarks.length > 0) {
            const userMarks = data.userMarks[0];
            const time = userMarks.test_date;
            const date = new Date(time * 1000);
            const options = {
                timeZone: "Asia/Kolkata",
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
            };

            document.getElementById('userMarks').innerHTML = `
                <h2 style="color: #0FB995;">User Marks</h2>
                <p><strong>Percentage:</strong> ${userMarks.grade}%</p>
                <p><strong>Total Marks:</strong> ${userMarks.total_mark}</p>
                <p><strong>Marks secured:</strong> ${userMarks.mark}</p>
                <p><strong>Total Time taken (minutes):</strong> ${userMarks.user_test_time}</p>
                <p><strong>Test taken (Date and Time):</strong> ${date.toLocaleString('en-US', options)} IST</p>
            `;
        } else {
            document.getElementById('userMarks').innerHTML = '<p style="color: red;">No Data Found</p>';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        loader.style.display = 'none';
        document.getElementById('userDetails').innerHTML = '';
        document.getElementById('userMarks').innerHTML = '';
        document.getElementById('error').textContent = 'There was a problem fetching the data. Please try again later.';
    });
});
