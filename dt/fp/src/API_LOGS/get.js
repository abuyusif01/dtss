const host = 'http://localhost:8000';


// create a function to fetch data from python api
const getData = async () => {

    let line_number = 1;
    let file_name = "api_log.csv";
    const response = await fetch(`${host}/get_data?line_number=${line_number}&file_name=${file_name}`);
    const data = await response.text();
    console.log(data);
    

}

getData();