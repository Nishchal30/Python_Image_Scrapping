from flask import Flask, request, render_template, jsonify
import requests
from urllib.request import urlopen
import logging, os
from bs4 import BeautifulSoup as bs
import pymongo

logging.basicConfig(filename="imgscrapping.log", level=logging.INFO, format='%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def home():

    logging.info("The flow reached to the home route")
    return render_template('index.html')


@app.route('/scrap', methods = ['POST', 'GET'])
def scrap():
    logging.info("The flow reached to the scrap route")
    if request.method == 'POST':
        try:
            save_dir = 'images/'
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            logging.info("The directory is created")

            query = request.form['search_for'].replace(" ", "")

            # fake user agent to avoid getting blocked by Google
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

            response = requests.get(f"https://www.google.com/search?q={query}&tbm=isch&source=lnms&sa=X&ved=2ahUKEwib1ZT6jbmAAxXgcmwGHRQYCmUQ0pQJegQIDhAB&biw=1366&bih=625&dpr=1")

            html_page = bs(response.content, "html.parser")

            all_images = html_page.find_all("img")
            del all_images[0]
            img_data = []

            for index, img in enumerate(all_images):
                image_url = img['src']
                image_data = requests.get(image_url).content

                mydict = {"Index" : index, "Image" : image_data}
                img_data.append(mydict)

                with open(os.path.join(save_dir, f"{query}_{all_images.index(img)}.jpg"), "wb") as f:
                    f.write(image_data)

            logging.info("The images are saved to the directory")

            client = pymongo.MongoClient("mongodb+srv://Nishchal30:Nishchal30@cluster0.9omin78.mongodb.net/")
            database = client['Image_scrapping']
            collection = database['Images']

            collection.insert_many(img_data)
            logging.info("The images are loaded to the Mongo DB")

            return "The data is scrapped and loaded"
        
        except Exception as e:
            print(e)
            logging.info(e)

    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run()