// === 1. Exam Control Variables ===
let tabSwitchCount = 0;
const maxTabSwitches = 2;
let examSubmitted = false;
let totalTime = 2 * 60; // Example: 2 minutes

// Run script after page loads completely
window.onload = function () {
    const timerElement = document.getElementById("timer");
    const examForm = document.querySelector("form");  // Get the exam form
    const modal = document.getElementById("customModal");
    const modalMessage = document.getElementById("modalMessage");

    if (!timerElement || !examForm || !modal || !modalMessage) {
        console.error("Required elements not found! Check your HTML.");
        return;
    }

    // === 2. Timer Setup (Starts countdown when page loads) ===
    function updateTimer() {
        if (examSubmitted) return; // Stop timer if exam is already submitted
        if (totalTime <= 0) {
            submitExam("⏳ Time is up! Exam submitted automatically.");
        } else {
            timerElement.innerText = formatTime(totalTime);
            totalTime--;
            setTimeout(updateTimer, 1000);
        }
    }

    // === 3. Tab Switching Detection ===
    document.addEventListener("visibilitychange", function () {
        if (document.hidden) {
            tabSwitchCount++;
            if (tabSwitchCount >= maxTabSwitches) {
                submitExam("🚫 Exam submitted due to excessive tab switching.");
            }
        }
    });

    // === 4. Function to Submit Exam Immediately ===
    function submitExam(message) {
        if (!examSubmitted) {
            examSubmitted = true;
            showCustomAlert(message);
            setTimeout(() => {
                examForm.submit();
            }, 3000); // Delay for alert display
        }
    }

    // === 5. Styled Alert Box ===
    function showCustomAlert(msg) {
        modalMessage.innerHTML = msg;
        modal.style.display = "block";
    }

    // === 6. Utility: Format Time (MM:SS) ===
    function formatTime(seconds) {
        let min = Math.floor(seconds / 60);
        let sec = seconds % 60;
        return `${min}:${sec < 10 ? "0" : ""}${sec}`;
    }

    // Start Timer
    updateTimer();
};
