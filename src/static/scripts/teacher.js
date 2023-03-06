const settingsButton = document.getElementById('settings-button');
const studentsButton = document.getElementById('students-button');

const allowChatCheckbox = document.getElementById('allow-chat');
const allowLogsCheckbox = document.getElementById('allow-logs');
const settingsForm = document.getElementById('settings-form');

const studentsList = document.getElementById('students-list');
const settings = document.getElementById('settings');

function showSettings() {
    studentsList.style.display = 'none';
    settings.style.display = 'block';
}

function showStudents() {
    studentsList.style.display = 'block';
    settings.style.display = 'none';
}

settingsButton.addEventListener('click', showSettings)
studentsButton.addEventListener('click', showStudents)

allowChatCheckbox.addEventListener('click', () => {
    sendSettings();
});

allowLogsCheckbox.addEventListener('click', () => {
    if (!allowLogsCheckbox.checked) {
        allowChatCheckbox.checked = false;
    }

    sendSettings();
});

function sendSettings() {
    fetch(window.location.pathname + '/settings', {
        method: 'POST',
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({chat: allowChatCheckbox.checked, logs: allowLogsCheckbox.checked})
    })
}