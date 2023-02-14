const classroom = document.getElementById('classroom');
const open = document.getElementById('open');
const chooseRole = document.getElementById('choose-role');
const loginForm = document.getElementById('login-form');

function classroomClicked(event) {
    window.location.pathname = '/login/classroom';
}

function openClicked(event) {
    chooseRole.style.display = 'none';
    loginForm.style.display = 'block';
}

classroom.addEventListener('click', classroomClicked);
open.addEventListener('click', openClicked);