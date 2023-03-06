const actionLink = document.getElementsByClassName('action')[0];
const modal = document.getElementById('myModal')
console.log(actionLink.id)
function actionClicked(event) {
    modal.style.display = 'block';  
}

actionLink.addEventListener('click', actionClicked)