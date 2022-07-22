from flask import Flask, render_template, request, session
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from pandas.io.json import json_normalize
import csv
import os
import json #Turn json to dict
# Sentiment analysis function using VADER
def vader_sentiment_scores(data_frame):
    # Define SentimentIntensityAnalyzer object of VADER.
    SID_obj = SentimentIntensityAnalyzer()
 
    # calculate polarity scores which gives a sentiment dictionary,
    # Contains pos, neg, neu, and compound scores.
    sentiment_list = []
    for row_num in range(len(data_frame)):
        sentence = data_frame['Review Text'][row_num]
        
        if sentence == None:
            sentiment_list.append('N/A')
            continue
        polarity_dict = SID_obj.polarity_scores(sentence)
 
        # Calculate overall sentiment by compound score
        if polarity_dict['compound'] >= 0.05:
            sentiment_list.append("Positive")
 
        elif polarity_dict['compound'] <= - 0.05:
            sentiment_list.append("Negative")
 
        else:
            sentiment_list.append("Neutral")
 
    data_frame['Sentiment'] = sentiment_list
 
    return data_frame
 
 
#*** Backend operation
# Read comment csv data
# df = pd.read_csv('data/comment.csv')
 
# WSGI Application
# Provide template folder name
# The default folder name should be "templates" else need to mention custom folder name
app = Flask(__name__, template_folder='templates')
 
app.secret_key = 'Yuelin'
 
#store the none type csv first
app.current_file_json = None
# @app.route('/')
# def welcome():
#     return "Ths is the home page of Flask Application"
 
@app.route('/')
def index():
    return render_template('index_upload_and_show_data.html')
 
@app.route('/',  methods=("POST", "GET"))
def uploadFile():
    if request.method == 'POST':
        uploaded_file = request.files['uploaded-file']
        df = pd.read_csv(uploaded_file)
        #Drop the NaN Text Review
        df = df[df['Review Text'].notna()]

        #session['uploaded_csv_file'] = df.to_json()
        #store cookie
        app.current_file_json=df.to_json()
        return render_template('index_upload_and_show_data_page2.html')
 
@app.route('/show_data')
def showData():
    # Get uploaded csv file from session as a json value
    #uploaded_json = session.get('uploaded_csv_file', None)
    uploaded_json =app.current_file_json
    if uploaded_json == None:
        return render_template('index_upload_and_show_data_page3.html')
    
    # Convert json to data frame
    #print(json.loads(uploaded_json)) # Debug
    uploaded_df = pd.DataFrame.from_dict(json.loads(uploaded_json))
    # Convert dataframe to html format
    uploaded_df_html = uploaded_df.to_html()
    return render_template('show_data.html', data=uploaded_df_html)
 
@app.route('/sentiment')
def SentimentAnalysis():
    # Get uploaded csv file from session as a json value
    #uploaded_json = session.get('uploaded_csv_file', None)
    uploaded_json=app.current_file_json
    # Convert json to data frame
    uploaded_df = pd.DataFrame.from_dict(json.loads(uploaded_json))
    # Apply sentiment function to get sentiment score
    uploaded_df_sentiment = vader_sentiment_scores(uploaded_df)
    # Show percentage of the review in POS/NEG/NET
    sentiment=pd.DataFrame() 
    total=uploaded_df_sentiment['Sentiment'].count()
    sentiment['Positive']=[f"{round(100 * uploaded_df_sentiment['Sentiment'].value_counts()['Positive'] / total,2)}%" ] 
    sentiment['Negative']=[f"{round(100 * uploaded_df_sentiment['Sentiment'].value_counts()['Negative'] / total,2)}%" ]
    sentiment['Neutral']=[f"{round(100 * uploaded_df_sentiment['Sentiment'].value_counts()['Neutral'] / total,2)}%" ]
    sentiment_df_html =sentiment.to_html()
    uploaded_df_html = uploaded_df_sentiment.to_html()
    return render_template('show_data.html', data=uploaded_df_html,sentiment=sentiment_df_html)
 
if __name__=='__main__':
    app.run(debug = True)