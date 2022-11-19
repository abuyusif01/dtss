
let plc_logs_table = document.querySelector("#plc_logs_table");

const get_data = (host, port, route, table, id) => {
    var data = new XMLHttpRequest();
    data.open("GET", `http://${host}:${port}/${route}?file_name=api_log.csv&line_number=${id}`);
    data.send();

    data.onreadystatechange = function () {
        if (data.readyState == 4 && data.status == 200) {
            var row = table.insertRow(1)
            var timestamp = row.insertCell(0)
            var from_addr = row.insertCell(1)
            var to_addr = row.insertCell(2)
            var label = row.insertCell(3)
            var port = row.insertCell(4)
            var bytes = row.insertCell(5)
            var status = row.insertCell(6)

            // conver this to json, easier to work with
            var temp = JSON.parse(data.responseText.replaceAll("'", '"'))
            timestamp.innerHTML = temp["Timestamp"]
            from_addr.innerHTML = temp["From"]
            to_addr.innerHTML = temp["To"]
            label.innerHTML = temp["Label"]
            bytes.innerHTML = temp["Value"]
            port.innerHTML = temp["Port"]

            // console.log(get_status("localhost", "8000", "get_data", "localhost", "8001", "get_status", "rf", table, id))

        }
    }
}

const get_status = (mhost, mport, mroute, shost, sport, sroute, model_name, table, id) => {
    var data = new XMLHttpRequest();
    var result = new XMLHttpRequest();

    data.open("GET", `http://${mhost}:${mport}/${mroute}?file_name=measurements.csv&line_number=${id}`);
    data.send();

    data.onreadystatechange = function () {
        if (data.readyState == 4 && data.status == 200) {
            var control_vars = ["model_name", "tank_liquidlevel", "flowlevel", "bottle_liquidlevel", "motor_status"]

            // convert this to json, easier to work with
            var temp = JSON.parse(data.responseText.replaceAll("'", '"'))
            result.open("GET", `http://${shost}:${sport}/${sroute}?${control_vars[0]}=${model_name}&${control_vars[1]}=${temp["tank_liquidlevel"]}&${control_vars[2]}=${temp["flowlevel"]}&${control_vars[3]}=${temp["bottle_liquidlevel"]}&${control_vars[4]}=${temp["motor_status"]}`);
            result.send();

            result.onreadystatechange = function () {
                if (result.readyState == 4 && result.status == 200) {
                    var temp = JSON.parse(result.responseText.replaceAll("'", '"'));
                    table.rows[id].cells[6].innerHTML = temp["result"];

                }
            }
        }
    }
}

export { get_data, get_status }