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



allowChatCheckbox.addEventListener('clicked', () => {
    settingsForm.submit();
});

allowLogsCheckbox.addEventListener('clicked', () => {
    if (!allowLogsCheckbox.checked) {
        allowChatCheckbox.checked = false;
    }

    settingsForm.submit();
});