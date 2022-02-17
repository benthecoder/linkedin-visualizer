# Linkedin Connections Insights 🪄

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/benthecoder/linkedin-visualizer/main/app.py)

Get helpful statistics on your LinkedIn connection now!

Read the article to know more about this project: [Visualize your LinkedIn Network with Python](https://medium.com/bitgrit-data-science-publication/visualize-your-linkedin-network-with-python-59a213786c4)

![streamlit app gif](media/app.gif)

## Features

This app tells you the information below

- Total connections on LinkedIn
- Where most of your connections work at
- Who most of your connections are (what job title they hold)
- Who you last connected with
- Who you first connected with (send them a message!)
- Bar chart of top companies and positions
- Time series plot of your connections over time (find out when you had the most connections)
- A graph/network of your connections (see your connections in a graph)
- Last but not least, a "who you can cold email" section that provides a list of emails of your connections (perks of LinkedIn connections!)

[Use it now!](https://share.streamlit.io/benthecoder/linkedin-visualizer/main/app.py)

## Images

![stats](media/app/stats.png)
![barchart](media/app/barchart.png)
![timeseries](media/app/timeseries.png)
![network](media/app/network.png)

## How to get the data?

First head over to the home page and click on your profile image

<img src="media/guide/1.png" width="400">

Click on the settings

<img src="media/guide/2.png" height="400">

Head to the data privacy tab

<img src="media/guide/3.png" height="400">

Find "Get a copy of your data"

![1](media/guide/4.png)

Click on connections only

![1](media/guide/5.png)

Click request archive and type your LinkedIn password

![1](media/guide/6.png)'

Now just wait a few minutes and the archive will arrive to your mail!
![1](media/guide/7.png)

Once you get the data, just drag it to the file uploader and enjoy the insights :)

## Run Locally

Clone the project

```bash
  git clone https://github.com/benthecoder/linkedin-visualizer.git
```

Go to the project directory

```bash
  cd linkedin-visualizer
```

Create Conda environment

```bash
  conda create --name env_name python=3.8
```

Activate the environment

```bash
  conda activate env_name
```

Install requirements

```bash
  pip install -r requirements.txt
```

Run streamlit

```bash
  streamlit run app.py
```

## Contributing

Contributions are always welcome!

## License

[MIT](https://choosealicense.com/licenses/mit/)
