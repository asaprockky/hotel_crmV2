document.addEventListener("DOMContentLoaded", function () {
    const today = new Date();
    const currentDay = today.getDate();
    const datesDiv = document.querySelector('.dates');

    for (let i = -3; i <= 3; i++) {
        let day = currentDay + i;
        let span = document.createElement('span');
        span.textContent = day;

        if (i === 0) {
            span.classList.add('today'); // Add class to highlight today
        }

        datesDiv.appendChild(span);
    }
});


document.addEventListener("DOMContentLoaded", function () {
    // Get today's date
    const now = new Date();
    
    // Format date (e.g., "20 December")
    const options = { day: 'numeric', month: 'long' };
    const formattedDate = now.toLocaleDateString('en-US', options);

    // Format time (e.g., "12:35 pm")
    const formattedTime = now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit', 
        hour12: true 
    });

    // Set the date
    document.getElementById("current-date").textContent = formattedDate;

    // Set the time
    document.getElementById("current-time").textContent = formattedTime;
});
