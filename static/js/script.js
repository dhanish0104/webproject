// Toast Helper (Robust)
function showToast(message, type = "info") {
    // Fallback if Toastify is not loaded (e.g. offline/network issue)
    if (typeof Toastify === 'undefined') {
        alert(message);
        return;
    }

    let backgroundColor;
    if (type === "success") backgroundColor = "linear-gradient(to right, #00b09b, #96c93d)";
    else if (type === "error") backgroundColor = "linear-gradient(to right, #ff5f6d, #ffc371)";
    else backgroundColor = "linear-gradient(to right, #3498db, #6dd5fa)";

    Toastify({
        text: message,
        duration: 3000,
        close: true,
        gravity: "top", // `top` or `bottom`
        position: "center", // `left`, `center` or `right`
        style: {
            background: backgroundColor,
            borderRadius: "8px",
            boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
        },
        stopOnFocus: true // Prevents dismissing of toast on hover
    }).showToast();
}

async function sendOTP() {
    let aadhaar = document.getElementById("aadhaar").value;
    let phone = document.getElementById("phone").value;
    let email = document.getElementById("email").value;
    let otpBtn = document.getElementById("otp-btn");

    if (!aadhaar || !phone || !email) {
        showToast("Please fill all fields first (Aadhaar, Phone, Email)", "error");
        return;
    }

    otpBtn.innerText = "Sending...";
    otpBtn.disabled = true;

    try {
        const response = await fetch('/send-otp', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: email, aadhaar: aadhaar, phone: phone })
        });

        const result = await response.json();
        console.log("OTP Response:", result);

        if (result.success) {
            // ... (rest of the success handling remains the same)
            // Show OTP in toast if returned (Dev Mode / Fallback)
            if (result.dev_otp) {
                showToast(`OTP: ${result.dev_otp} (Email failed)`, "info");
            } else {
                showToast(result.message, "success");
            }

            document.getElementById("otp-section").style.display = "block";
            document.getElementById("login-btn").style.display = "block";

            // Start 60s Countdown for Resend
            let timeLeft = 60;
            otpBtn.disabled = true;
            otpBtn.style.display = "inline-block"; // Ensure it stays visible for countdown

            let timerId = setInterval(() => {
                otpBtn.innerText = `Resend in ${timeLeft}s`;
                timeLeft--;

                if (timeLeft < 0) {
                    clearInterval(timerId);
                    otpBtn.innerText = "Resend OTP";
                    otpBtn.disabled = false;
                }
            }, 1000);

        } else {
            showToast("Error: " + result.message, "error");
            otpBtn.innerText = "Send OTP";
            otpBtn.disabled = false;
        }
    } catch (error) {
        console.error('Error:', error);
        showToast("Failed to send request.", "error");
        otpBtn.innerText = "Send OTP";
        otpBtn.disabled = false;
    }
}

async function login() {
    let aadhaar = document.getElementById("aadhaar").value;
    let phone = document.getElementById("phone").value;
    let email = document.getElementById("email").value;
    let otp = document.getElementById("otp").value;

    if (!otp) {
        showToast("Please enter the OTP", "error");
        return;
    }

    try {
        let response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                aadhaar: aadhaar,
                phone: phone,
                email: email,
                otp: otp
            })
        });
        let result = await response.json();

        if (result.success) {
            window.location.href = result.redirect;
        } else {
            showToast("Login Failed: " + result.message, "error");
        }
    } catch (error) {
        console.error('Error:', error);
        showToast("Failed to login.", "error");
    }
}

function goToComplaint(problem) {
    // Store in localStorage for client-side persistence if needed, 
    // but better to pass via URL parameter or store in simple way
    // For now keeping it simple as per original design, but adding href update
    window.location.href = "/complaint?problem=" + encodeURIComponent(problem);
}

function submitComplaint(event) {
    if (event) event.preventDefault();

    let btn = document.getElementById("submitBtn");
    btn.disabled = true;
    btn.innerText = "Submitting...";
    btn.classList.add("opacity-50", "cursor-not-allowed");

    // Get params from URL (source of truth for Category/Topic)
    const urlParams = new URLSearchParams(window.location.search);
    let categoryElem = document.getElementById("categoryName");
    let category = urlParams.get('category') || (categoryElem ? categoryElem.textContent : "");
    // 'description' param in URL is our Topic
    let topicElem = document.getElementById("topicName");
    let topic = urlParams.get('description') || (topicElem ? topicElem.textContent : "");

    let state = document.getElementById("state").value;
    let district = document.getElementById("district").value;
    let area = document.getElementById("area").value;
    let description = document.getElementById("description").value; // This is the textarea for user details

    fetch('/submit-complaint', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            category: category,
            topic: topic,
            state: state,
            district: district,
            area: area,
            description: description
        })
    })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showToast("✅ " + data.message, "success");
                setTimeout(() => {
                    window.location.href = "/dashboard";
                }, 1500); // Slight delay to let user see the toast
            } else {
                showToast("❌ Error: " + data.message, "error");
                btn.disabled = false;
                btn.innerText = "Submit Complaint";
                btn.classList.remove("opacity-50", "cursor-not-allowed");
            }
        })
        .catch(err => {
            console.error(err);
            showToast("Submission failed", "error");
            btn.disabled = false;
            btn.innerText = "Submit Complaint";
            btn.classList.remove("opacity-50", "cursor-not-allowed");
        });
}
