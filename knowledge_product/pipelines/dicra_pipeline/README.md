# DiCRA Insight generator

## Prerequisite

- Download Positive and Negative Deviance files from https://dicra.nabard.org/jharkhand/ and copy extracted files in dicra_data folder

## Setup

```
virtualenv venv --python=python3
source venv/bin/activate
pip install -r requirements.txt
```

## Runing the code

- Replace <Your-API-key> with your own OpenAI api key in main.py
- Make sure you have files in dicra_data folder, and dicra_insights folder exists

```
python3 main.py
```


## Results

insights files will be generated in the dicra_insights folder with <district-name>.txt