const classroom = document.getElementById('classroom');
const open = document.getElementById('open');
const chooseRole = document.getElementById('choose-role');
const signUpForm = document.getElementById('signup-form');
const classroomRedirect = document.getElementById('classroom-redirect');

function classroomClicked(event) {
    chooseRole.style.display = 'none';
    classroomRedirect.style.display = 'block';
}

function openClicked(event) {
    chooseRole.style.display = 'none';
    signUpForm.style.display = 'block';
}

classroom.addEventListener('click', classroomClicked);
open.addEventListener('click', openClicked);