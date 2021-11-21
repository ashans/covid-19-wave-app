# Covid-19 dashboard app

Covid-19 dashboard build using [H2O Wave framework](https://wave.h2o.ai)

<img src="./static/demo.gif" width="600" height="338" alt="Demo"/>

## Running this App Locally

### System Requirements 
1. Python 3.6+
2. pip3

### 1. Run the Wave Server
Follow the documentation to [download and run](https://wave.h2o.ai/docs/installation) the Wave Server on your local machine.<br>
For macOS run the following command to download and run H2O Wave server.
```shell script
make wave run-wave
```


### 2. Build the python environment
```shell script
make setup
```

### 3. Run the application
```shell script
make run
```

### 4. View the application
Go to http://localhost:10101/covid from browser