# Solar Panel Efficiency Calculator 
 
 
This Project is a Flask Application used for querying, storing, and returning information from the Solar radiation Database. 

In this repository you are going to find 3 directories: src, data, and kurbenetes
you are also going to have a Dockerfile and a docker-compose.yaml used for containerization.

## Data
The data used in this project is located in the folder called "Data" where it contains five json files, 4 files are data from 4 different cities in texas Austin, Dallas, Houston and San Antonio. In this folder you are also going to get Solar json file where all the solar data will be located and a dumb rdb file.

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



# Running flask_api.py


| Routes                               | Method | Description                                                                                                          |
|-------------------------------------|--------|----------------------------------------------------------------------------------------------------------------------|
| /image                              | POST   | Creates a plot of the locus groups of the gene data and stores the image in redis                                     |
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



