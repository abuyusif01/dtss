import { get_data, get_status } from './utils.js'

var plc_logs_head = [
    { Timestamp: "", From: "", To: "", Label: "", Port: "", Value: "", Status: "" }
];

var events_head = [
    { Timestamp: "", Name: "", Role: "", Range: "", Message: "" }
];


const plc_logs_table = document.querySelector("#plc_logs_table");
const events_table = document.querySelector("#events_hightlight");
const recent_update = document.createElement('div')

const plc_data = Object.keys(plc_logs_head[0]);
const event_data = Object.keys(events_head[0]);
const var_events_hightlight = document.getElementById("events_hightlight");

const date = new Date()
const table_row_count = 13
const update_row_count = 7
const plc_addr = ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4", "10.0.0.5", "10.0.0.6", "10.0.0.7"]
const ports = ["8080", "9000", "4454", "443", "4444"]
const plc_status = ["Normal", "Dos", "Command Injection", "SQLi"]
const labels = ["Sensor Update", "Plc tag", "Value Update", "Resting", "Shutting Down"]
const names = ["Abuyusif01", "Admin", "xyz", "abc", "samha"]
const time = [2, 3, 4, 5, 6, 7, 8, 9, 10]
const ranges = ["Days", "Hours", "Minutes", "Seconds"]

const mhost = "localhost"
const mroute = "get_data"
const mport = "8000"
const shost = "localhost"
const sroute = "get_status"
const sport = "8001"
const model_name = "rf"


function gen_events(table) {
    var row = table.insertRow(1)
    var timestamp = row.insertCell(0)
    var name = row.insertCell(1)
    var role = row.insertCell(2)
    var range = row.insertCell(3)
    var msg = row.insertCell(4)

    timestamp.innerHTML = date
    name.innerHTML = names[Math.floor((Math.random() * 4))]
    role.innerHTML = "Admin"
    range.innerHTML = ranges[Math.floor((Math.random() * 3))]
    msg.innerHTML = "Updated PLC Tag"

}

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

if (plc_logs_table !== null) {

    var get_status_count = 1;
    var get_data_count = 1;
    var get_data_cell_number = 0;

    generateTableHead(plc_logs_table, plc_data);

    
    // timeout to update plc logs table is .5 seconds
    setInterval(() => {
        document.getElementById("round-1").setAttribute("data-percent", "90");

        /*
            First row in the dataset is the header
            omit it and start from the second row
        */
        get_status_count < 1
            ? (get_status_count = 1)
            : (get_status_count = get_status_count);

        /*
            Apparently js is all about tricks, there's no clear way of doing things
            get_status will double request data from Logs API
            then send that data to ML API and get the status
        */
        get_status(mhost,
            mport,
            mroute,
            shost,
            sport,
            sroute,
            model_name,
            plc_logs_table,
            parseInt(get_status_count),
            get_data_cell_number,
            get_data_count
        );
        get_data(mhost, mport, mroute, plc_logs_table, get_data_count);
        
        ++get_data_count;
        ++get_data_cell_number;
        /*
            This is just a trick to get the accurate data
            since each row in the measurement represents 4 row in the data
            we gonna force the data to be 4 times the measurement
            basically fetching one line in measuremnt == fetching 4 lines in data
        */
        get_status_count = get_data_count / 4;

    }, 1000);

} else if (events_table !== null) {
    generateTableHead(events_table, event_data);
    for (i = 0; i < table_row_count; i++) {
        gen_events(var_events_hightlight);
    }
    var rowCount = document.getElementById('events_hightlight').rows.length;
    document.getElementById('message_count').innerHTML = rowCount - 1;
}

document.getElementById("updates").appendChild(recent_update)

function gen_update(id, name, time, range, msg, img) {
    div = document.createElement('div')
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
// for (i = 0; i < update_row_count; i++)
//     gen_update("updates", names[Math.floor((Math.random() * 4))], time[Math.floor((Math.random() * 8))],
//         ranges[Math.floor((Math.random() * 3))], "Updated PLC Tag", "profile-1.jpg")
