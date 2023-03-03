const promptBox = document.getElementById('prompt-box');
const list = document.getElementById('list');
const submit = document.getElementById('submit');

async function say() {
    let prompt = promptBox.value;

    let element = document.createElement('div');

    list.appendChild(element)

    element.innerHTML = `<p>You: ${prompt}</p>
    <p>Chatbot: thinking...</p>
    <br><br><br>`

    let response = await fetch('./api', {
        body: prompt
    });

    let output = await response.text();

    element.innerHTML = `<p>You: ${prompt}</p>
    <p>Chatbot: ${output}</p>
    <br><br><br>`
}

submit.addEventListener('click', say);