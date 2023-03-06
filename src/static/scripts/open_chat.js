const promptBox = document.getElementById('prompt-box');
const list = document.getElementById('list');
const submit = document.getElementById('submit');

list.scrollTop = list.scrollHeight;

async function say() {
    let prompt = promptBox.value;

    let element = document.createElement('div');

    list.appendChild(element)

    element.innerHTML = `<p>You: ${prompt}</p>
    <p>Chatbot: thinking...</p>
    <br><br><br>`

    promptBox.value = '';
    list.scrollTop = list.scrollHeight;

    let response = await fetch(window.location.pathname + '/api', {
        method: 'POST',
        body: prompt
    });

    let output = await response.text();

    element.innerHTML = `<p>You: ${prompt}</p>
    <p>Chatbot: ${output}</p>
    <br><br><br>`
    list.scrollTop = list.scrollHeight;
}

submit.addEventListener('click', say);