### Solar Panel Efficiency Calculator 
 
 
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
 
 1. You will need to access all the files from the Kurbenetes folder 
 2. Create a docker image 
 ```
  docker build . -t <docker_hub_username>/solar_app:01
 ```
