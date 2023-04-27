# Solar Panel Efficiency Calculator 
 
 
This Project is a Flask Application used for querying, storing, and returning information from the Solar radiation Database. 

## Data
The data used in this project is located in the folder called "Data" where it contains five json files, 4 files are data from 4 different cities in Texas (Austin, Dallas, Houston and San Antonio). In this folder you are also going to get Solar.json file where all the solar data will be located and a dumb rdb file. The data used in this program can be found at [this link](https://www.visualcrossing.com/weather-data).

## Installation
To set up this project, enter this command:
```
git clone https://github.com/JakeWendling/SolarPanelEfficiencyCalculator.git
cd SolarPanelEfficiencyCalculator
```
## Docker Container 

## Building an Image 
In order to customize the code to suit your requirements, creating a personal image is an option that you can explore. It's necessary to create an account on Docker Hub and then proceed to upload your Docker Image to it. This can be accomplished by following the steps outlined below:
 
 1. You will need to access all the files from the Kubernetes folder and change the username to your Dockerhub account name
 2. Create the docker image 
 ```
   docker build . -t <docker_hub_username>/solar_app:01
 ```
 3. As you created the new image you will have to go into the Kubernetes folder and change the "..api-deployment.yml" image to you new image <docker_hub_username>/solar_app:01
 4. Also repeat this step but in the solar-app-wrk-deployment.yml file 
 5. Now that the image is created it is important to push it 
 ```
    docker push
 ```
 
 ## Kubernetes
 also known as "K8s" is an open-source container orchestration system that automates the deployment, scaling, and management of containerized applications.
 To start the application on your computer/server:

 ```
 kubectl apply -f kubernetes/
 ```
All of the Kubernetes services are initiated. You then will see an output confirming this services were configured .

## Running flask_api.py


| Routes                               | Method | Description                                                                                                          |
|-------------------------------------|--------|----------------------------------------------------------------------------------------------------------------------|
| /data                               | POST   | Gets the weather/solar panel data and saves the data in dictionary format in the flask app. Returns a String          |
|                                     | GET    | Gets the weather data and returns the data in dictionary format                                                       |
|                                     | DELETE | Deletes the data stored in the redis db returns a success message                                                     |
| /cities                             | GET    | Gets the weather data and returns the list of cities                                                                   |
| /weather/cities                     | GET    | Returns a dateList a list of cities (strings) for which weather data is available                                     |
| /weather/cities/&lt;city&gt;              | GET    | Gets the weather data and returns the data for a given city                                                            |
| /weather/cities/&lt;city&gt;/dates        | GET    | Gets the weather data and returns the list of dates in a list                                                          |
| /weather/cities/&lt;city&gt;/dates/&lt;date&gt; | GET    | Gets the weather data, then returns the weather data for a given date/city, if available. Otherwise returns an error message and error code. |
| /weather/categories | GET | Gets the weather data, then returns the categories for weather data of a given date/city, if available. |
| /weather/cities/&lt;city&gt;/categories/&lt;category&gt;| GET |Gets the weather data, then returns the weather data of a given category for a given city, if available. |
| /solar | GET | Gets the solar data from the data base|
| /solar/categories | GET | Gets the list od categories in the solar data base|
| /solar/categories/&lt;category&gt;| GET | Gets the specific category of a given category in the solar data base|
| /jobs | GET | Returns a list of submitted jobs |
| /jobs/&lt;id&gt; | GET | Returns info about the given job |
| /jobs/&lt;id&gt;/results -o <filename> | GET | Returns the results of the given job in %lt;filename&gt; |
| /jobs -d \@<filename> | POST | Uploads a job from <filename> to the application |

## Commands 

## /data
To load the data into the app, run the following:
```
  curl -X POST jakew57.coe332.tacc.cloud/data
```

To delete the data from the app, run the following:
```
  curl -X DELETE jakew57.coe332.tacc.cloud/data
```

To request the entire dataset:
```
 curl jakew57.coe332.tacc.cloud/data
```
This method will display something as follows: 
```
{
  "latitude" : 30.2676,
  "longitude" : -97.743,			
  "resolvedAddress" : "Austin, TX, United States",
  "address" : "Austin"...
```

## /cities
To get the list of cities:
```
  curl jakew57.coe332.tacc.cloud/cities 
```
By curling into the cities route you should get:
```
Dallas,
Austin,
Houston,
San_Antonio
```

## /weather/cities
To access a list of cities (strings) for which weather data is available:
```
  curl jakew57.coe332.tacc.cloud/weather/cities
```
The resultant output should look the same as the above /cities:

## /weather/cities/&lt;city&gt;
If you are only interested in finding the data fromm a specific city you can curl:
```
  curl jakew57.coe332.tacc.cloud/weather/cities/&lt;city&gt;
```
This should give you something like:
```
[
  {
    "cloudcover": "45.7",
    "conditions": "Partially cloudy",
    "datetime": "2023-01-01",.....
  
```
You can also add a start and end date to limit the data using the following command:
```
curl jakew57.coe332.tacc.cloud/weather/cities/&lt;city&gt;?start=&lt;start_date&gt;&end=&lt;end_date&gt;
```
Make sure to enter this command surrounded by quotes, or the shell will interpret the command incorrectly.

## /weather/cities/&lt;city&gt;/dates
To Get the weather data see the list of dates in a list
    
```
 curl jakew57.coe332.tacc.cloud/weather/cities/&lt;city&gt;/dates

```
Your output should look like:

```
[
  "2023-01-01",
  "2023-01-02",
  "2023-01-03",
  "2023-01-04",
  "2023-01-05",.....
```


## /weather/cities/&lt;city&gt;/dates/&lt;date&gt;
This route gets the data from a specific date from the list provided:
```
  curl jakew57.coe332.tacc.cloud/weather/cities/&lt;city&gt;/dates/&lt;date&gt;
```
Your output should look like:
```
{
  "cloudcover": "22.2",
  "conditions": "Partially cloudy",
  "datetime": "2023-04-13",
  "datetimeEpoch": "1681362000",.....
```

##categories go here

You can also add a start and end date to limit the data using the following command:
```
curl "jakew57.coe332.tacc.cloud/weather/cities/&lt;city&gt;?start=&lt;start_date&gt;&end=&lt;end_date&gt;"
```
Make sure to enter this command surrounded by quotes, or the shell will interpret the command incorrectly.


## /jobs
To create a plot of the of the data, first modify job.json to your liking, then post it to the application:

To get a graph of the weather data, use this format. Replace city with one of the cities listed above and put a category from /weather/categories
```json
{
        "type":"graphWeather",
        "param": {		
	        "city":"Dallas",
	        "category":"temp"
	}
}
```
To get a graph of the solar panel efficiency for your city, use this format. Replace city with one of the cities listed above:
```json
{
        "type":"graphEfficiency",
        "param":"Dallas"
}
```
Then post the job.json:
```
  curl -X POST jakew57.coe332.tacc.cloud/jobs -d \@job.json
```
This will return something like the following:
```
{
  "id": "38b2a9c1-375b-4d43-8edf-9c64344c3c72",
  "param": "Dallas",
  "start": "2023-04-27 00:59:27.009889",
  "status": "submitted",
  "type": "graphEfficiency"
}
```
The job id will be the id shown above with "job." infront: (Ex: "job.38b2a9c1-375b-4d43-8edf-9c64344c3c72") 
To get the image of a plot:
```
  curl jakew57.coe332.tacc.cloud/jobs/<jobid>/results -o plot.png 
```
Now you can view the image on your computer at plot.png.

## solar/
To access the solar route:
```
  curl jakew57.coe332.tacc.cloud/solar
```
expected output should look like:
```
{
  "CIGS": {
  "Cost": "Low",
  "Efficiency": "0.14",
  "Size": "Average, thin-film",
  "T_Coeff": "-0.0028"......
```


## /solar/categories
To access the list of categories in the 
```
  curl jakew57.coe332.tacc.cloud/solar/categories
```
expected output should look like:
```
[
  "Efficiency",
  "Size",
  "Cost",
  "T_Coeff"
]
```
## /solar/categories/&lt;category&gt;
```
  curl jakew57.coe332.tacc.cloud/solar/categories/&lt;category&gt;
```
expected output should look like for the Efficiency category:
```
{
  "CIGS": "0.14",
  "CdTe": "0.1",
  "Monocrystalline": "0.2",
  "PERC": "0.25",
  "Polycrytalline": "0.16",
  "a-Si": "0.07"
}
```

