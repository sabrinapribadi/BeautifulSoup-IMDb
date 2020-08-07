from flask import Flask, render_template 
import pandas as pd
import requests
from bs4 import BeautifulSoup 
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')


app = Flask(__name__) #don't change this code

def scrap(url):
    #This is fuction for scrapping
    url_get = requests.get(url)
    soup = BeautifulSoup(url_get.content,"html.parser")
    
    #Find the key to get the information
    table = soup.find('div', attrs={'class':'lister-list'}) 
    tr = table.find_all('div', attrs={'class':'lister-item mode-advanced'})

    title = [] #initiating a tuple
    imdb_ratings = [] #initiating a tuple
    metascores = [] #initiating a tuple
    votes = [] #initiating a tuple

    for i in tr:
        # The name
        movie_title = i.h3.a.text
        title.append(movie_title)
        # The IMDB rating
        imdb = i.strong.text
        imdb_ratings.append(imdb)
        # The Metascore
        if i.find('div', class_ = 'ratings-metascore') is not None:
          m_score = i.find('span', class_ = 'metascore').text
          metascores.append(m_score)
        else:
          m_score = 0
          metascores.append(m_score)
        # The number of votes
        vote = i.find('span', attrs = {'name':'nv'})['data-value']
        votes.append(vote)

    #creating the dataframe
    df = pd.DataFrame({
    'movie': title,
    'imdb': imdb_ratings,
    'metascore': metascores,
    'votes': votes
    }) 

   #data wranggling -  try to change the data type to right data type

    df['imdb'] = df['imdb'].astype('float')
    df['imdb'] = df['imdb']*10
    df['metascore'] = df['metascore'].astype('int')
    df['votes'] = df['votes'].astype('int')

   #end of data wranggling

    return df

@app.route("/")
def index():
    df = scrap('http://imdb.com/search/title/?release_date=2019-01-01,2019-12-31') #insert url here

    #This part for rendering matplotlib
    best7 = df.sort_values('votes', ascending=False).head(7)
    fig = plt.figure(figsize=(13,7),dpi=300)
    plt.plot( 'movie', 'imdb', data=best7, marker='|', markerfacecolor='blue', markersize=12, color='skyblue', linewidth=4)
    plt.plot( 'movie', 'metascore', data=best7, marker='x', color='olive', linewidth=2)
    plt.title('imdb score vs metascore')
    plt.legend()
    
    #Do not change this part
    plt.savefig('plot1',bbox_inches="tight") 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    #this is for rendering the table
    df = df.to_html(classes=["table table-bordered table-striped table-dark table-condensed"])

    return render_template("index.html", table=df, result=result)


if __name__ == "__main__": 
    app.run()
