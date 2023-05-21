import pymongo
import pandas as pd
import streamlit as st
import snscrape.modules.twitter as sn_twitter

# header name
st.header(':blue[_Twitter Scraping_]')

# image = Image.open('logo.jpeg')
# creating two tabs
tab1, tab2 = st.tabs(["Home", "About"])


# converting dataframe to csv file
def convert_to_csv(scrap_data):
    return scrap_data.to_csv().encode('utf-8')


# converting dataframe to json file
def convert_to_json(scrap_data):
    return scrap_data.to_json(orient='index')


# Home tab
with tab1:
    # creating form to get variables
    with st.form(key='form1'):
        search_name = st.text_input("search keyword/#tag")
        search_level = st.slider("Select the level", 0, 1000, step=100)
        start_date = st.date_input('From')
        end_date = st.date_input('Till')
        submit_button = st.form_submit_button(label="submit")
    # using session_state to avoid steamlit app reinitiate problem while clicking button
    if "load_state" not in st.session_state:
        st.session_state.load_state = False
    scrap_data = pd.DataFrame()
    if submit_button or st.session_state.load_state:
        st.session_state.load_state = True

        j = 0
        # using for loop to scrap data with keyword&date
        for tweet in sn_twitter.TwitterSearchScraper(
                f'{search_name} since:{start_date} until:{end_date}').get_items():
            if j == search_level:
                break
            # append through dataframe
            # date, id, url, tweet content, user,reply count, retweet count,language, source, like count
            scrap_data = scrap_data.append({'date': tweet.date, 'id': tweet.id, 'url': tweet.url,
                                            'tweetcontent': tweet.rawContent,
                                            'user': tweet.user.username
                                               , 'replycount': tweet.replyCount,
                                            'retweetcount': tweet.retweetCount
                                               , 'language': tweet.lang, 'source': tweet.source,
                                            'likecount': tweet.likeCount}, ignore_index=True)
            j = j + 1
    st.write(scrap_data)
    csv_file = convert_to_csv(scrap_data)
    json_file = convert_to_json(scrap_data)
    client = pymongo.MongoClient(
        "mongodb+srv://kalin:1234@scrapping.ah9c9dv.mongodb.net/?retryWrites=true&w=majority")
    tw_db = client.kalin
    tw_col = tw_db.scrapping
    scrap_data.reset_index(inplace=True)
    scrap_dict = scrap_data.to_dict("records")
    upload = st.button('upload')
    if "load_state" not in st.session_state:
        st.session_state.load_state = False

    if upload:
        st.session_state.load_state = True
        tw_col.delete_many({})
        tw_col.insert_many(scrap_dict)
        st.success('Uploaded to Database', icon="✅")

    # download as csv file
    if st.download_button(label="Download data as CSV", data=csv_file
            , file_name='tweet_scrap_data_csv.csv', mime='text/csv'):
        st.success('Download Successful', icon="✅")

    # download as json file
    if st.download_button(label="Download data as JSON", data=json_file
            , file_name='tweet_scrap_data_json.js', mime='text/js'):
        st.success('Download Successful', icon="✅")

# About tab
with tab2:
    st.write('This app is for scraping the data from Twitter. You can Scrap the data like '
             '(date, id, url, tweet content, user,reply count, retweet count,language'
             ', source, like count etc) from twitter.')
    st.subheader('Snscraper')
    st.write('Here snscrape is used to scrape tweets from'
             'Twitters API without any restrictions or request limits. Moreover, you '
             'dont even need a Twitter developer account to scrape tweets when you use snscrape.')
    st.subheader('MongoDB')
    st.write('With MongoDB here you can upload the scraped data and as we know MongoDB is '
             'much more than a database. It’s a complete developer data platform. '
             'And with MongoDB Atlas, the cloud offering by MongoDB, Hepls us to '
             'establish connection and store data. ')
    st.subheader('Download_files')
    st.write('Here you can download the scraped data with csv format and json format')
