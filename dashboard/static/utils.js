const get_data = (host, port, table) => {
    var table_req = new XMLHttpRequest();
    var card_req = new XMLHttpRequest();

    /*
        curl 'http://localhost:8000/get_data?file_name=api_log.csv&line_number=1'
        Output:
        {
            'Timestamp': '2022-11-18 16:51:04.377093', 
            'From': '10.0.0.1', 
            'To': '10.0.0.2', 
            'Label': 'SENSOR2-FL', 
            'Port': '44818', 
            'Value': '10.0',
            'Status': 'Normal'
        }

    */
    table_req.open("GET", `http://${host}:${port}/gen_table?file_name=table.csv`);

    table_req.send();

    table_req.onreadystatechange = function () {
        if (table_req.readyState == 4 && table_req.status == 200) {
            var row = table.insertRow(1)
            var timestamp = row.insertCell(0)
            var from_addr = row.insertCell(1)
            var to_addr = row.insertCell(2)
            var label = row.insertCell(3)
            var port = row.insertCell(4)
            var bytes = row.insertCell(5)
            var status = row.insertCell(6)

            // conver this to json, easier to work with
            var temp = JSON.parse(table_req.responseText.replaceAll("'", '"'))
            timestamp.innerHTML = temp["Timestamp"]
            from_addr.innerHTML = temp["From"]
            to_addr.innerHTML = temp["To"]
            label.innerHTML = temp["Label"]
            bytes.innerHTML = temp["Value"]
            port.innerHTML = temp["Port"]
            status.innerHTML = temp["Status"]
        }
    }

    card_req.open("GET", `http://${host}:${port}/card_info`);
    card_req.send();
    card_req.onreadystatechange = function () {

        if (card_req.readyState == 4 && card_req.status == 200) {
            var result = JSON.parse(card_req.responseText.replaceAll("'", '"'))
            document.getElementById("network_hero").innerHTML = parseInt(result["network_count"])
            document.getElementById("network_plabel").innerHTML = parseInt(result["network_percent"]).toFixed(2) + "%"

            document.getElementById("injection_hero").innerHTML = parseInt(result["injection_count"])
            document.getElementById("injection_plabel").innerHTML = parseInt(result["injection_percent"]).toFixed(2) + "%"


        }
    }
}


function user_info(host, port) {
    var req = new XMLHttpRequest();

    req.open("GET", `http://${host}:${port}/userInfo`, true);
    req.send();
    req.onreadystatechange = function () {
        if (req.readyState == 4 && req.status == 200) {
            var result = JSON.parse(req.responseText)
            document.getElementById("name").innerHTML = result["name"].charAt(0).toUpperCase() + result["name"].slice(1);
            document.getElementById("role").innerHTML = result["role"].charAt(0).toUpperCase() + result["role"].slice(1);
        }
    }
}

export { get_data, user_info }