const searchBar = document.getElementById('school-search-bar');
const schoolList = document.getElementById('school-system-list');

let stopTypingTimeout = 0;

async function stopTypingTimeoutEnd() {
    let searchBarContent = searchBar.value;

    if (searchBarContent.length < 1) {
        return;
    }

    const response = await fetch(`/login/classroom/api?search=${searchBarContent}`);
    
    if (response.status != 200) {
        alert(`An error occured. Error code: ${response.status}`);
        return;
    }

    const json = await response.json();

    schoolList.innerHTML = '';

    for (const key of Object.keys(json)) {
        let link = document.createElement('a');
        link.innerHTML = key;
        link.href = `/login/classroom/${json[key]}`;

        schoolList.appendChild(link);
        schoolList.appendChild(document.createElement('br'))
    }
}

async function searchBarChanged(event) {
    clearTimeout(stopTypingTimeout);
    stopTypingTimeout = setTimeout(stopTypingTimeoutEnd, 100);
}

searchBar.addEventListener('input', searchBarChanged)