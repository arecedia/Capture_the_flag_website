//
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("loginForm");
    const submitBtn = document.getElementById("submitBtn");
    const identifier = document.getElementById("identifier")
    const password = document.getElementById("password")
    const feedbackMessage = document.getElementById("feedbackMessage");

    // Attach even listener to the form submission
    form.addEventListener("submit", function (event){
        event.preventDefault(); // Prevent default form submission (through page reloading)

        // loading message
        feedbackMessage.textContent = "Submitting...";
        const formData = new FormData(form);

        // Create a JSON object from the form data
        const data = {};
        formData.forEach((value, key) => {
            data[key] = value;
        });

        // Use fetch API to submit the form data asynchronously
        fetch("/login.html", {
            method: "POST", // Submit through post request
            headers: {
                "Content-Type": "application/json" // Tells the server that we are submitting JSON data
            },
            body: JSON.stringify(data), // Convert form data to JSON
        })
            .then(response => response.json())
            .then(data => {
                // If login was successful
                if (data.success) {
                    feedbackMessage.textContent = "Login Successful! Redirecting...";
                    feedbackMessage.style.color = "green";
                    window.location.href = data.redirect_url || "http://127.0.0.1:8000"
                } else {
                    feedbackMessage.textContent = data.message || "An error occurred. Please try again."
                    feedbackMessage.style.color = "red";
                }
            })
            .catch(error => {
                // Handle errors
                console.error("Error:", error);
                feedbackMessage.textContent = "An error occurred. Please try again.";
                feedbackmessage.style.color = "red";
            })
            .finally(() => {
                submitBtn.disabled = false;
            });

        // Disable the submit button to prevent multiple clicks
        submitBtn.disabled = true;
    });
});