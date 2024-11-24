// Function to update notification count
function updateNotificationCount() {
    fetch(notificationCountUrl)  
        .then(response => response.json())
        .then(data => {
            const notificationCount = document.querySelector('.notification-count');
            notificationCount.textContent = data.count;

            if (data.count === 0) {
                notificationCount.style.display = 'none'; // Hide if 0 notifications
            } else {
                notificationCount.style.display = 'inline'; // Show if there are notifications
            }
        })
        .catch(error => console.error('Error:', error));
}

// Function to load notifications
function loadNotifications() {
    fetch(notificationListUrl)  
        .then(response => response.text())
        .then(html => {
            const notificationList = document.querySelector('.notification-list');
            notificationList.innerHTML = html;
        })
        .catch(error => console.error('Error:', error));
}

document.addEventListener('DOMContentLoaded', function () {
    const notificationBtn = document.querySelector('.notification-btn');
    const notificationDropdown = document.querySelector('.notification-dropdown');

    // Update notification count when page loads
    updateNotificationCount();

    // Show/hide notifications and load them when clicking the bell icon
    notificationBtn.addEventListener('click', function () {
        if (notificationDropdown.style.display === 'none' || notificationDropdown.style.display === '') {
            notificationDropdown.style.display = 'block';  // Show dropdown
            loadNotifications();  // Load notifications
        } else {
            notificationDropdown.style.display = 'none';  // Hide dropdown
        }
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function (event) {
        if (!notificationBtn.contains(event.target) && !notificationDropdown.contains(event.target)) {
            notificationDropdown.style.display = 'none';
        }
    });
});
