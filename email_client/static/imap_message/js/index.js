const host = window.location.host;
const url_ws = 'ws://' + host + '/ws/bar/';
const progressBar = document.getElementById('progress-bar');
const progressInfo = document.getElementById('progress-info');
const table_body = document.getElementById('table_body');
let gameSocket = new WebSocket(url_ws);

gameSocket.onmessage = updateProgressBar;

function updateProgressBar(msg) {
let msgJSON = JSON.parse(msg.data);
if (msgJSON.type === 'completed') {
    progressInfo.textContent = msgJSON.message;
    progressBar.value = msgJSON.progress;
}
else if (msgJSON.type === 'progress') {
    console.log(msgJSON.progress);
    progressInfo.textContent = msgJSON.message;
    progressBar.value = msgJSON.progress;
    if (msgJSON.content !== null) {
        createRowTable(msgJSON.content)
    }

}}

function createRowTable (obj) {
    let row = document.createElement('tr');
    for  (let key in obj) {
        let cell = document.createElement('td');
        cell.textContent = obj[key];
        row.appendChild(cell);
    }
    table_body.insertBefore(row, table_body.firstChild)
}