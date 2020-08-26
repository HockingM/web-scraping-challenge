from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import scrape_mars


# create an instance of Flask
app = Flask(__name__)

# use PyMongo to establish Mongo connection
mongo = PyMongo(app, uri="mongodb://localhost:27017/mars_app")

# route to render index.html template using data from Mongo
@app.route("/")
def home_page():

    # find one record of data from the mongo database
    mars_data = mongo.db.collection.find_one()
        
    # return template and data
    return render_template("index.html", mars=mars_data)


# route that will trigger the scrape function
@app.route("/scrape")
def scrape():

    # run the news scrape function
    news_data = scrape_mars.scrape_news()

    # run the hemisphere scrape function
    hemisphere_image_urls = scrape_mars.scrape_hemispheres()

    # update dictionary for hemisphere scrape
    for i in range(len(hemisphere_image_urls)):
        news_data.update(hemisphere_image_urls[i])

    # run the mars facts scrape function
    mars_facts = scrape_mars.scrape_facts()

    # update dictionary for mars facts scrape
    news_data["mars_facts"] = mars_facts

    # update the Mongo database using update and upsert=True
    mongo.db.collection.drop()
    mongo.db.collection.update({}, news_data, upsert=True)
   
    # redirect back to home page
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)