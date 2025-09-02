# Bandcamp-Collection-Exporter
Small python tool to scrape your bandcamp collection and store all the data in a github gist so you can embed it in any way you wish!


instructions!:

download the .py script and save it anywhere you can easily find it

firstly you put in your bandcamp username in the USERNAME variable

then you log into bandcamp and inspect your browser cookies for "identity" and "session" and copy their values into the COOKIES variable

then you create a github token with gist permissions and put it in the GITHUB_TOKEN variable

finally you can either create a gist manually and put its ID in the GIST_ID variable or leave it as None and the script will create a new gist for you 

then in a command prompt in the folder you saved the script in, just type "python bandcampexport.py"
