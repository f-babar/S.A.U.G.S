# S.A.U.G.S (Sentiment Analysis Using Geographical Segmentation)

This project is implemented in Python & Angular 7 to find the sentiment polarity of tweets and visualize them on map to show that what people think about a particular topic geographically. 

## Installation & Development Setup
1. Clone the repo   

```sh
git clone https://github.com/f-babar/S.A.U.G.S.git

Make sure that you alrady have installed the `python`, `npm` and `mongoDB` on your system.

```
2. Go to the `S.A.U.G.S/saugs-server` directory and run the following command to install the server dependencies/libraries

```sh
>> pip install -r requirements.txt

```
Execute the `mongo.py` file with the following command. It will insert all the contries and cities list in MongoDB
```sh
>> python mongo.py
```

Now, finally run the server by executing the `index.py` file. Server will be started and RESTFul API's will be accessible.

3. After running the server, now run the front-end application which is developed in Angular. Install the node_modules first by running `npm install`.

Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.

## Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory. Use the `--prod` flag for a production build.


