# Solar Panel Efficiency Calculator 
 
 
This Project is a Flask Application used for querying, storing, and returning information from the Solar radiation Database. 

In this repository you are going to find 3 directories: src, data, and kurbenetes
you are also going to have a Dockerfile and a docker-compose.yaml used for containerization.

## Data
The data used in this project is located in the folder called "Data" where it contains five json files, 4 files are data from 4 different cities in texas Austin, Dallas, Houston and San Antonio. In this folder you are also going to get Solar json file where all the solar data will be located and a dumb rdb file. The data used in this program can be found at [this link](https://www.visualcrossing.com/weather-data) you just have to type the name of the cities you want to locate in our case was the cities mentioned above 

## Installation
To set up this project, follow these steps: clone the repository and make a new directory to hold the data.

```
  git clone git@github.com:JakeWendling/SolarPanelEfficiencyCalculator.git
```
## Docker Container 

## Building an Image 
In order to customize the code to suit your requirements, creating a personal image is an option that you can explore. It's necessary to create an account on Docker Hub and then proceed to upload your Docker Image to it. This can be accomplished by following the steps outlined below:
 
 1. You will need to access all the files from the Kurbenetes folder and change the username to your Dockerhub account name
 2. Create the docker image 
 ```
   docker build . -t <docker_hub_username>/solar_app:01
 ```
 3. As you created the new image you will have to go into the Kurbenetes folder and change the "..api-deployment.yml" image to you new image <docker_hub_username>/solar_app:01
 4. Also repeat this step but in the solar-app-wrk-deployment.yml file 
 5. Noe that the image is created is important to push it 
 ```
    docker push
 ```
 
 ## Kurbenetes
 also known as "K8s" is an open-source container orchestration system that automates the deployment, scaling, and management of containerized applications.

 ```
  kubectl apply -f solar-app-api-deployment.yml
  kubectl apply -f solar-app-api-ingress.yml
  kubectl apply -f solar-app-api-nodeport.yml
  kubectl apply -f solar-app-db-deployment.yml
  kubectl apply -f solar-app-db-pvc.yml
  kubectl apply -f solar-app-db-service.yml
  kubectl apply -f solar-app-wrk-deployment.yml
 ```
Two Kubernetes services are initiated; one for the Flask application and another for the Redis database. During the maiden run, the data download process might take a while to complete. You then will see an output confirming this services were configured 



## Running flask_api.py


| Routes                               | Method | Description                                                                                                          |
|-------------------------------------|--------|----------------------------------------------------------------------------------------------------------------------|
| /image                              | POST   | Creates a plot of the data and stores the image in redis                                     |
|                                     | GET    | Returns an image of a plot image as bytes                                                                             |
|                                     | DELETE | Deletes the image stored in the redis db returns a successful string                                                  |
| /data                               | POST   | Gets the weather/solar panel data and saves the data in dictionary format in the flask app. Returns a String          |
|                                     | GET    | Gets the weather data and returns the data in dictionary format                                                       |
|                                     | DELETE | Deletes the data stored in the redis db returns a success message                                                     |
| /cities                             | GET    | Gets the weather data and returns the list of cities                                                                   |
| /weather/cities                     | GET    | Returns a dateList a list of cities (strings) for which weather data is available                                     |
| /weather/cities/&lt;city&gt;              | GET    | Gets the weather data and returns the data for a given city                                                            |
| /weather/cities/&lt;city&gt;/dates        | GET    | Gets the weather data and returns the list of dates in a list                                                          |
| /weather/cities/&lt;city&gt;/dates/&lt;date&gt; | GET    | Gets the weather data, then returns the weather data for a given date/city, if available. Otherwise returns an error message and error code. |
| /weather/categories | GET | Gets the weather data, then returns the categories for weather data of a given date/city, if available. |
|/weather/cities/&lt;city&gt;/categories/&lt;category&gt;| GET |Gets the weather data, then returns the weather data of a given category for a given city, if available. |
| /solar | GET | Gets the solar data from the data base|
| /solar/categories | GET | Gets the list od categories in the solar data base|
| /solar/categories/&lt;category&gt;| GET | Gets the specific category of a given category in the solar data base|
## Commands 

## /data
To load the data into the app, run the following:
```
  curl -X POST localhost:5000/data
```

To delete the data from the app, run the following:
```
  curl -X DELETE localhost:5000/data
```

To request the entire dataset:
```
 curl localhost:5000/data
```
This method will display something as follows: 
```

!!DISPLAY DATA ROUTE 
SOMETHING HERE !!


```

## /cities
To get the list of cities:
```
  curl localhost:5000/cities 
```
By curling into the cities route you should get:
```
  !!DISPLAY CITIES ROUTE!!

```

## /weather/cities
To access a list of cities (strings) for which weather data is available:
```
  curl localhost:5000/weather/cities
```
The resultant output should look as:
```
  !!! DISPLAY /weather/cities!!! 

```

## /weather/cities/&lt;city&gt;
If you are only interested in finding the data fromm a specific city you can curl:
```
  curl localhost:5000/weather/cities/&lt;city&gt;
```
This should give you something like:
```
  !!! DISPLAY weather/cities/&lt;city&gt; !!!
  
```

## /weather/cities/&lt;city&gt;/dates
To Get the weather data see the list of dates in a list
    
```
 curl localhost:5000/weather/cities/&lt;city&gt;/dates

```
your output may look as:

```
!!DISPLAY /weather/cities/&lt;city&gt;/dates !
```


## /weather/cities/&lt;city&gt;/dates/&lt;date&gt;
This route gets the data from a specific date from the list provided:
```
  curl localhost:5000/weather/cities/&lt;city&gt;/dates/&lt;date&gt;
```
Your output mayl ook as:
```
!!!DISPLAY /weather/cities/&lt;city&gt;/dates/&lt;date&gt; !!


```

## /image 
To create a plot of the of the data:
```
  curl -X POST localhost:5000/image
```

To delete the image from the data base:
```
  curl -X DELETE localhost:5000/image
```

To get the image of a plot as bytes:
```
  curl localhost:5000/image 
```

It is important to know that you can download the image into the python pod:
```
  curl localhost:5000/image --output plot.png
```

## solar/
To access the solar route:
```
  curl localhost:5000/solar
```
expected output should look like:
```
     DISPLAY HERE
     DISPLAY HERE
```


## /solar/categories
To access the list of categories in the 
```
  curl localhost:5000/solar/categories
```
expected output should look like:
```
  DISPLAY HERE
  DISPLAY HERE
```
## /solar/categories/&lt;category&gt;
```
  curl localhost:5000/solar/categories/&lt;category&gt;
```
expected output should look like:
```
  DISPLAY HERE
  DISPLAY HERE
```

