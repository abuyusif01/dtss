import { get_data, user_info, get_event, term_info, user_data } from './utils.js'

var plc_logs_head = [
    { Timestamp: "", From: "", To: "", Label: "", Port: "", Value: "", Status: "" }
];

var events_head = [
    { Timestamp: "", ID: "", Desc: "", IP: "", Trriggered: "", Priority: "" }
];


const plc_logs_table = document.querySelector("#plc_logs_table");
const events_table = document.querySelector("#events_hightlight");
const _index = document.querySelector("#_index");
const _about = document.querySelector("#_about");
const _terminal = document.querySelector("#_terminal");
const _settings = document.querySelector("#_settings");
const _events = document.querySelector("#_events");

const recent_update = document.createElement('div')
const plc_data = Object.keys(plc_logs_head[0]);
const update_row_count = 7
const names = ["Abuyusif01", "Admin", "xyz", "abc", "samha"]
const time = [2, 3, 4, 5, 6, 7, 8, 9, 10]
const ranges = ["Days", "Hours", "Minutes", "Seconds"]

let host = ""
location.hostname === "localhost" ? host = "localhost" : host = location.hostname // get server url
const port = "8000" // logs api port
let server_port = ""
location.hostname === "localhost" ? server_port = "5001" : server_port = "80" // get server url
const term_port = "8003" //term donut api port

function generateTableHead(table, data) {
    let thead = table.createTHead();
    let row = thead.insertRow();
    for (let key of data) {
        let th = document.createElement("th");
        let text = document.createTextNode(key);
        th.appendChild(text);
        row.appendChild(th);
    }
}

if (_index !== null) {
    generateTableHead(plc_logs_table, plc_data);
    setInterval(() => {
        get_data(host, port, plc_logs_table, 1);
    }, 500);

} else if (_events !== null) {
    setInterval(() => {
        get_data(host, port, plc_logs_table, 0);
    }, 500);
    get_event(host, 5001, events_table);

} else if (_terminal !== null) {
    setInterval(() => {
        term_info(host, term_port);
    }, 1000);

} else if (_settings !== null) {
    user_data(host, server_port);
    setInterval(() => {
        get_data(host, port, plc_logs_table, 0);
    }, 500);
}

user_info(host, server_port);
document.getElementById("updates").appendChild(recent_update)
// move this to utils
function gen_update(id, name, time, range, msg, img) {
    let div = document.createElement('div')
    div.innerHTML = `<div class="update">
<div class="profile-photo">
    <img src="./images/${img}">
</div>
    <div class="message">
        <p>
            <b>${name}</b> 
            ${msg}
        </p><small class="text-muted">
            ${time} 
            ${range} Ago
        </small>
    </div>
</div>`;
    document.getElementById(id).appendChild(div)
}

for (let i = 0; i < update_row_count - 1; i++)
    gen_update("updates", names[Math.floor((Math.random() * 4))], time[Math.floor((Math.random() * 8))],
        ranges[Math.floor((Math.random() * 3))], "Updated PLC Tag", "profile-1.jpg")
