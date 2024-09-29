// Handle disturbance and demo video playback logic
const disturbanceVideo = document.getElementById('disturbance-video');
const avatarVideo = document.getElementById('avatar-video');

// Hardcoded video paths
const idleVideoUrl = '/static/videos/WIN_20240927_19_23_19_Pro.mp4';  // Idle video path
const demoVideoUrl = '/static/videos/test_video.mp4';  // Demo video path

let playDisturbanceInterval;  // Declare disturbance interval globally

// Initially hide the disturbance video
disturbanceVideo.style.display = 'none';

// Function to show disturbance effect
function playDisturbance(callback) {
    disturbanceVideo.style.display = 'block';  // Show the disturbance video
    disturbanceVideo.play();  // Play the short disturbance video

    // Hide disturbance video after it finishes (assuming 0.5 seconds duration)
    setTimeout(() => {
        disturbanceVideo.style.display = 'none';  // Hide the video after it plays

        if (callback) callback();  // Execute callback if provided (e.g., switching to another video)
    }, 500);  // Adjust this time if your disturbance video has a different duration
}

// Function to continuously play disturbance video every 10 seconds
function startDisturbanceLoop() {
    playDisturbance();  // Play disturbance immediately on page load
    playDisturbanceInterval = setInterval(playDisturbance, 10000);  // Play disturbance every 10 seconds
}

// Function to switch to demo videos (with sound enabled)
function playDemoVideo() {
    // Clear the response box and print a message
    const message = 'Find out more here: https://john-john.nu/about';
    typeResponseTextWithSpeech(message, null, 50);  // No audio for this message

    // Play disturbance effect before switching to first demo video
    playDisturbance(() => {
        // Switch to first demo video (test_video.mp4)
        avatarVideo.src = demoVideoUrl;  // Set source to the first demo video
        avatarVideo.muted = false;  // Unmute demo video to enable sound
        avatarVideo.loop = false;  // Ensure demo video doesn't loop
        avatarVideo.play();

        // When the first demo video ends, play the second demo video
        avatarVideo.onended = function() {
            // Play disturbance before switching to the second demo video
            playDisturbance(() => {
                // Switch to the second demo video (test_video_2.mp4)
                const secondDemoVideoUrl = '/static/videos/test_video_2.mp4';  // Second demo video path
                avatarVideo.src = secondDemoVideoUrl;
                avatarVideo.play();

                // When the second demo video ends, switch back to the idle video
                avatarVideo.onended = function() {
                    // Play disturbance again after the second demo ends
                    playDisturbance(() => {
                        // Switch back to idle video after disturbance
                        avatarVideo.src = idleVideoUrl;
                        avatarVideo.loop = true;  // Idle video should loop
                        avatarVideo.muted = true;  // Mute the idle video
                        avatarVideo.play();
                    });
                };
            });
        };
    });
}

// Start disturbance effect loop on page load
window.onload = function() {
    startDisturbanceLoop();  // Start disturbance loop when the page loads
};

// Function to handle both typing effect and speech playback
function typeResponseTextWithSpeech(responseText, audioUrl, speed = 50) {
    let index = 0;
    const responseDiv = document.getElementById('avatar-response');
    responseDiv.textContent = '';  // Clear previous content

    // Function to handle text typing
    function typeNextLetter() {
        if (index < responseText.length) {
            responseDiv.textContent += responseText.charAt(index);  // Add next character
            index++;
            responseDiv.scrollTop = responseDiv.scrollHeight;  // Auto-scroll to bottom
            setTimeout(typeNextLetter, speed);  // Recursively call with variable delay
        }
    }

    // Start typing effect
    typeNextLetter();

    // Play the audio
    if (audioUrl) {
        const audio = new Audio(audioUrl);
        audio.play();
    }
}

// Function to submit form and handle response
function submitForm() {
    let userInput = document.getElementById('user-input').value.trim().toLowerCase();

    // Clear the input field after submission
    document.getElementById('user-input').value = '';  // Clear input box

    // Check if the user input contains the word "demo"
    if (userInput.includes('demo')) {
        // Play the demo video sequence
        playDemoVideo();
    } else {
        // Send the request to the Flask server for other inputs
        fetch('/get_response', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ 'user_input': userInput })
        })
        .then(response => response.json())
        .then(data => {
            if (data.response && data.audio_url) {
                typeResponseTextWithSpeech(data.response, data.audio_url, 50);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}


// Event listeners for form submission
document.getElementById('input-form').addEventListener('submit', function (e) {
    e.preventDefault();  // Prevent page reload on form submission
    submitForm();  // Trigger form submission
});

document.getElementById('user-input').addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();  // Prevent a new line from being added
        submitForm();  // Trigger form submission
    }
});
