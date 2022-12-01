## API FOR SERVER LOGS AND REAL TIME SYSTEM LOGGING

### 1. Introduction

This API is mainly used to generate table for dashboard. The folder contains 2 python files. first is the main api second is Utils files. The utils file automate the procedure of generating the table by retrieving and sending measurements to ML API which later on we'll use to get Network status.

The API read data from the followings files:

1. `measurements.csv`: This file contains the data from the PLCs and sensors.
2. `api_log.csv`: This file contains the logs from the PLCs.
3. `table.csv`: This file contains the data from the PLCs and sensors combine with result from the ML models API. Hence this file is ready to be displayed by user on the dashboard.


### 2. Installation

This API is built using Python 3.10.8: for installation and running the API, please follow the steps below:

1. Clone the repository `git clone https://github.com/abuyusif01/dtss`
2. Create a virtual environment `python3 -m venv log_api`
3. Install the requirements `python3 -m pip3 install -r requirements.txt`
4. Run the API `python app.py`
5. Run Utils `python utils.py` - This file requires a database to be up and running.

```mysql

create table users (role varchar(255) not null, email varchar(255) not null, password varchar(255) not null);
create table attacks (name varchar(255) not null, value varchar(255), );

```


### 3. API

The API has 3 endpoints:

1. gen_table: This end point is used to generate the table for the dashboard, the route take the following as input parameters:

    - `file_name`: the name of the file to be read (default `table.csv`)

2. get_data: This end point is used as helper function for `gen_table` to get the data from csv files, the route take the following as input parameters:

    - `file_name`: the name of the file to be read (default `measurements.csv`)
    - `line_number`: the line number to be read (default `1`)

3. card_info: This end point is used to get the data for the card on the dashboard, we read the values from database and return them as json object.



### 4. Usage

#### 4.1. gen_table

```bash

    curl 'http://localhost:8000/gen_table?file_name=table.csv'

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
```

#### 4.2. get_data

```bash

    curl 'http://localhost:8000/get_data?file_name=measurements.csv&line_number=1'

    Output: 
    {
        "Timestamp": temp[0],
        "tank_liquidlevel": temp[1],
        "flowlevel": temp[2],
        "bottle_liquidlevel": temp[3],
        "motor_status": temp[4],
    }


    curl 'http://localhost:8000/get_data?file_name=api_log.csv&line_number=1'

    Output:

    {
        "Timestamp": temp[0],
        "From": temp[1],
        "To": temp[2],
        "Label": temp[3],
        "Port": temp[4],
        "Value": temp[5],
    }

```

#### 4.3. card_info

```bash

    curl 'http://localhost:8000/card_info'

    Output:
    {
        "network_count": network_count,
        "network_percent": network_percent,
        "injection_count": injection_cont,
        "injection_percent": injection_percent,
        "total_lines": total_lines,
    }

```
