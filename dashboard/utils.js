const get_data = (host, port, route, table, id) => {
    var data = new XMLHttpRequest();

    /*
        curl 'http://localhost:8000/get_data?file_name=api_log.csv&line_number=1'
        Output:
        {
            'Timestamp': '2022-11-18 16:51:04.377093', 
            'From': '10.0.0.1', 
            'To': '10.0.0.2', 
            'Label': 'SENSOR2-FL', 
            'Port': '44818', 
            'Value': '10.0'
        }

    */
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
            var status = row.insertCell(6) // never used in this function, we gonna use it in the status function

            // conver this to json, easier to work with
            var temp = JSON.parse(data.responseText.replaceAll("'", '"'))
            timestamp.innerHTML = temp["Timestamp"]
            from_addr.innerHTML = temp["From"]
            to_addr.innerHTML = temp["To"]
            label.innerHTML = temp["Label"]
            bytes.innerHTML = temp["Value"]
            port.innerHTML = temp["Port"]
        }
    }
}


const get_status = (mhost, mport, mroute, shost, sport, sroute, model_name, table, id, count) => {
    var data = new XMLHttpRequest();
    var result = new XMLHttpRequest();
    var attack_count = 0;

    /*
        curl 'http://localhost:8000/get_data?file_name=measurements.csv&line_number=1'

        Here is the sample response from the above request
        {
            Timestamp: '2022-10-10 16:04:56.160129', 
            tank_liquidlevel: '5.8', 
            flowlevel: '0.0', 
            bottle_liquidlevel: '0.0', 
            motor_status: '0'
        }
    */
    data.open("GET", `http://${mhost}:${mport}/${mroute}?file_name=measurements.csv&line_number=${id}`);
    data.send();

    data.onreadystatechange = function () {
        if (data.readyState == 4 && data.status == 200) {
            var injection_count = parseInt(document.getElementById("injection_hero").innerHTML) + 1;
            var network_count = parseInt(document.getElementById("network_hero").innerHTML) + 1;
            var control_vars = ["model_name", "tank_liquidlevel", "flowlevel", "bottle_liquidlevel", "motor_status"]
            var temp = JSON.parse(data.responseText.replaceAll("'", '"'))

            /*
                request to the ML API and get the result
                curl 'http://localhost:8001/get_status?model_name=rf&tank_liquidlevel=5.8&flowlevel=10.0&bottle_liquidlevel=0.0&motor_status=1'
                
                Here is an example of the response
                {
                    "result": "Normal"
                }
            */
            result.open("GET", `http://${shost}:${sport}/${sroute}?${control_vars[0]}=${model_name}&${control_vars[1]}=${temp["tank_liquidlevel"]}&${control_vars[2]}=${temp["flowlevel"]}&${control_vars[3]}=${temp["bottle_liquidlevel"]}&${control_vars[4]}=${temp["motor_status"]}`);
            result.send();

            /*
                percentage calculation
                for injection and network
                injection = (injection_count - 1 / count) * 100
                -1 because we start with 1, not 0

            */
            var injection_percent = ((injection_count - 1) / count) * 100
            isNaN(injection_percent) ? injection_percent = 0 : injection_percent = injection_percent

            var network_percent = ((network_count - 1) / count) * 100
            isNaN(network_percent) ? network_percent = 0 : network_percent = network_percent

            document.getElementById("network_plabel").innerHTML = network_percent.toFixed(2) + "%"
            document.getElementById("injection_plabel").innerHTML = injection_percent.toFixed(2) + "%"
            

            result.onreadystatechange = async function () {
                if (result.readyState == 4 && result.status == 200) {

                    var temp = JSON.parse(result.responseText.replaceAll("'", '"'));
                    // update the status column
                    table.rows[1].cells[6].innerHTML = temp["result"];

                    // update boxes
                    if (temp["result"] != "Normal") {
                        /*
                            PERCENTAGE OF THE BOXES (ID)
                            network_plabel 
                            injection_plabel
                            server_plabel
                        */

                        /*
                            HERO TEXT OF THE BOXES (ID)
                            injection_hero
                            network_hero
                            server_hero
                        */

                        if (temp["result"] == "Command Injection TL" || temp["result"] == "Command Injection TH") {

                            /*
                                we dublicate this code because we need to update the percentage and the hero text
                                even when the value didnt change
                                same goes for the network box
                            */
                            document.getElementById("injection_hero").innerHTML = injection_count
                            var percent = (injection_count / count) * 100
                            percent > 100 ? percent = 100 : percent = percent
                            document.getElementById("injection_plabel").innerHTML = percent.toFixed(2) + "%"

                            // call the api to send admin msg about this attack
                            // calculate the percentage of the box
                            // plot the percentage
                        }
                        else if (temp["result"] == "DoS") {
                            document.getElementById("network_hero").innerHTML = network_count

                            var percent = (network_count / count) * 100
                            percent > 100 ? percent = 100 : percent = percent
                            document.getElementById("network_plabel").innerHTML = percent.toFixed(2) + "%"

                        }
                        else if (temp["result"] == "Server Failure") {
                            // this not implemented yet
                            // make a route to ping all the servers and check if they are up
                            // plc1 do this and update it to the log file {need to create an extra column for this}

                        }
                    }
                }
            }
        }
    }
}

export { get_data, get_status }