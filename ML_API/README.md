## API FOR ML MODELS

### 1. Introduction

This API is used to get the predictions from the ML models. The API is built using Flask and the models are built using scikit-learn.
The folder contains the following files:

1. app.py - This file contains the code for the API.
2. train.ipynb - This file contains the code for training the models.
3. label.py - This file contains the code for the labelling attacks for the training data.


### 2. Installation

This API is built using Python 3.: for installation and running the API, please follow the steps below:

1. Clone the repository
2. Create a virtual environment
3. Install the requirements
4. Run the API


### 3. API

The API has 2 endpoints:

1. get_stutus: This end point is used to check the status of Digital Twin state, the route take the following as input parameters:

    - `tank_liquidlevel`: the liquid level of the tank capture by the sensor
    - `flowlevel`: sensor value for flow level
    - `bottle_liquidlevel`:  bottle liquid level captured from the sensor
    - `motor_status`: current status of plc1 motor valve
    - `model_name`: since we have a total of 5 models, we need to specify which model to use (default rf - random forest)

2. plc_log: This end point take only 1 argument which is a `file name` and return its content as a json object.



### 4. Models

The models are built using scikit-learn and are saved in the `models` folder. The models are:

1. `rf`: Random Forest
2. `stacking`: Stacking
3. `logistic`: Logistic
4. `GB`: Gradient Boosting
5. `nb`: naive bayes

The models are trained using the `train.ipynb` file and the data is stored in the `models` folder.


### 5. Usage


#### 5.1. get_status
``` bash
   
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
```

#### 5.2. plc_log
``` bash
   
    curl 'http://localhost:8000/plc_log?name=/etc/passwd'
    Output:
    {
        root:x:0:0::/root:/bin/bash
        bin:x:1:1::/:/usr/bin/nologin
        daemon:x:2:2::/:/usr/bin/nologin
        mail:x:8:12::/var/spool/mail:/usr/bin/nologin
        ftp:x:14:11::/srv/ftp:/usr/bin/nologin
        http:x:33:33::/srv/http:/usr/bin/nologin
        nobody:x:65534:65534:Nobody:/:/usr/bin/nologin
        dbus:x:81:81:System Message Bus:/:/usr/bin/nologin
        systemd-coredump:x:981:981:systemd Core Dumper:/:/usr/bin/nologin
        systemd-network:x:980:980:systemd Network Management:/:/usr/bin/nologin
        systemd-oom:x:979:979:systemd Userspace OOM Killer:/:/usr/bin/nologin
        systemd-journal-remote:x:978:978:systemd Journal Remote:/:/usr/bin/nologin
        systemd-resolve:x:977:977:systemd Resolver:/:/usr/bin/nologin
        systemd-timesync:x:976:976:systemd Time Synchronization:/:/usr/bin/nologin
        tss:x:975:975:tss user for tpm2:/:/usr/bin/nologin
        uuidd:x:68:68::/:/usr/bin/nologin
        avahi:x:973:973:Avahi mDNS/DNS-SD daemon:/:/usr/bin/nologin
        named:x:40:40:BIND DNS Server:/:/usr/bin/nologin
        brltty:x:972:972:Braille Device Daemon:/var/lib/brltty:/usr/bin/nologin
        dnsmasq:x:971:971:dnsmasq daemon:/:/usr/bin/nologin
        git:x:970:970:git daemon user:/:/usr/bin/git-shell
        nbd:x:969:969:Network Block Device:/var/empty:/usr/bin/nologin
        nm-openvpn:x:968:968:NetworkManager OpenVPN:/:/usr/bin/nologin
        ntp:x:87:87:Network Time Protocol:/var/lib/ntp:/bin/false
        openvpn:x:967:967:OpenVPN:/:/usr/bin/nologin
        polkitd:x:102:102:PolicyKit daemon:/:/usr/bin/nologin
        rpc:x:32:32:Rpcbind Daemon:/var/lib/rpcbind:/usr/bin/nologin
        rtkit:x:133:133:RealtimeKit:/proc:/usr/bin/nologin
        sddm:x:966:966:Simple Desktop Display Manager:/var/lib/sddm:/usr/bin/nologin
        usbmux:x:140:140:usbmux user:/:/usr/bin/nologin
        abuyusif01:x:1000:1000:abuyusif01:/home/abuyusif01:/bin/zsh
        geoclue:x:965:965:Geoinformation service:/var/lib/geoclue:/usr/bin/nologin
        mysql:x:963:963:MariaDB:/var/lib/mysql:/usr/bin/nologin
        rpcuser:x:34:34:RPC Service User:/var/lib/nfs:/usr/bin/nologin
        lightdm:x:962:962:Light Display Manager:/var/lib/lightdm:/usr/bin/nologin
        ldap:x:439:439:LDAP Server:/var/lib/openldap:/usr/bin/nologin
    }
```