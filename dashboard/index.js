let mountains = [
    { Timestamp: "", From: "", To: "", Label: "", Port: "", "Byte Count": "", Status: "" },

];



const date = new Date()
const plc_addr = ["10.0.0.1", "10.0.0.2", "10.0.0.3", "10.0.0.4", "10.0.0.5", "10.0.0.6", "10.0.0.7"]
const ports = ["8080", "9000", "4454", "443", "4444"]
const plc_status = ["Normal", "Dos", "Command Injection", "SQLi"]
const labels = ["Sensor Update", "Plc tag", "Value Update", "Resting", "Shutting Down"]

function insert_to_table(table) {
    var row = table.insertRow(1)
    var timestamp = row.insertCell(0)
    var from_addr = row.insertCell(1)
    var to_addr = row.insertCell(2)
    var label = row.insertCell(3)
    var port = row.insertCell(4)
    var bytes = row.insertCell(5)
    var status = row.insertCell(6)

    timestamp.innerHTML = date
    from_addr.innerHTML = plc_addr[Math.floor((Math.random() * 6))]
    to_addr.innerHTML = plc_addr[Math.floor((Math.random() * 6))]
    label.innerHTML = labels[Math.floor((Math.random() * 4))]
    bytes.innerHTML = Math.floor((Math.random() * 9000) + 1000)
    port.innerHTML = ports[Math.floor((Math.random() * 4))]
    status.innerHTML = plc_status[Math.floor((Math.random() * 3))]

}
// timestamp, fron, to, port, byte size, status

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

function generateTable(table, data) {
    for (let element of data) {
        let row = table.insertRow();
        for (key in element) {
            let cell = row.insertCell();
            let text = document.createTextNode(element[key]);
            cell.appendChild(text);
        }
    }
}

let table = document.querySelector("table");
let data = Object.keys(mountains[0]);
generateTableHead(table, data);
// generateTable(table, mountains);

let var_table = document.getElementById("plc_logs_table");

for (i = 0; i < 13; i++)
    insert_to_table(var_table);

let recent_update = document.createElement('div')

let names = ["Abuyusif01", "Admin", "xyz", "abc", "samha"]
let time = [2, 3, 4, 5, 6, 7, 8, 9, 10]
let range = ["Days", "Hours", "Minutes", "Seconds"]

document.getElementById("updates").appendChild(recent_update)

function gen_update(id, name, time, range, msg) {
    div = document.createElement('div')
    div.innerHTML = `<div class="update">
<div class="profile-photo">
    <img src="./images/profile-1.jpg">
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
for (i =0; i< 7; i++)
    gen_update("updates", names[Math.floor((Math.random() * 4))], time[Math.floor((Math.random() * 8))], range[Math.floor((Math.random() * 3))], "Updated PLC Tag")
