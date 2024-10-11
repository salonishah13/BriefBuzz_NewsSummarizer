import streamlit as st
from PIL import Image
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen
from newspaper import Article
import io
import nltk
from textblob import TextBlob

nltk.download('punkt')

st.set_page_config(page_title=' BriefBuzz 📰', page_icon='./Meta/newspaper.ico')


def fetch_news_search_topic(topic):
    try:
        formatted_topic = '+'.join(topic.split())  # Format topic for URL
        st.write(f"Fetching news for topic: {formatted_topic}")  # Debug statement
        site = 'https://news.google.com/rss/search?q={}'.format(formatted_topic)
        op = urlopen(site)  # Open that site
        rd = op.read()  # read data from site
        op.close()  # close the object
        sp_page = soup(rd, 'xml')  # scrapping data from site
        news_list = sp_page.find_all('item')  # finding news
        return news_list
    except Exception as e:
        st.error(f"Error fetching news for {topic}: {e}")
        return []


def fetch_top_news():
    site = 'https://news.google.com/news/rss'
    op = urlopen(site)  # Open that site
    rd = op.read()  # read data from site
    op.close()  # close the object
    sp_page = soup(rd, 'xml')  # scrapping data from site
    news_list = sp_page.find_all('item')  # finding news
    return news_list


def fetch_category_news(topic):
    site = 'https://news.google.com/news/rss/headlines/section/topic/{}'.format(topic)
    op = urlopen(site)  # Open that site
    rd = op.read()  # read data from site
    op.close()  # close the object
    sp_page = soup(rd, 'xml')  # scrapping data from site
    news_list = sp_page.find_all('item')  # finding news
    return news_list


def fetch_news_poster(poster_link):
    try:
        u = urlopen(poster_link)
        raw_data = u.read()
        image = Image.open(io.BytesIO(raw_data))
        st.image(image, use_column_width=True)
    except:
        image = Image.open('./Meta/no_image.jpg')
        st.image(image, use_column_width=True)


def display_news(list_of_news, news_quantity):
    c = 0
    for news in list_of_news:
        c += 1
        st.write('**({}) {}**'.format(c, news.title.text))
        news_data = Article(news.link.text)
        try:
            news_data.download()
            news_data.parse()
            news_data.nlp()
        except Exception as e:
            st.error(e)
        fetch_news_poster(news_data.top_image)
        with st.expander(news.title.text):
            st.markdown(
                '''<h6 style='text-align: justify;'>{}"</h6>'''.format(news_data.summary),
                unsafe_allow_html=True)
            st.markdown("[Read more at {}...]({})".format(news.source.text, news.link.text))
        st.success("Published Date: " + news.pubDate.text)
        if c >= news_quantity:
            break 


def summarize(url):
    try:
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()

        title = article.title
        authors = article.authors
        publish_date = article.publish_date
        summary = article.summary

        st.subheader("Summary")
        st.markdown(f"**Title:** {title}")
        st.markdown(f"**Authors:** {authors}")
        st.markdown(f"**Publication Date:** {publish_date}")
        st.markdown(f"**Summary:** {summary}")

        analysis = TextBlob(article.text)
        polarity = analysis.polarity
        sentiment = "positive" if polarity > 0 else "negative" if polarity < 0 else "neutral"

        st.subheader("Sentiment Analysis")
        st.markdown(f"**Polarity:** {polarity}")
        st.markdown(f"**Sentiment:** {sentiment}")
    except Exception as e:
        st.error(f"Error summarizing article: {e}")


def run():
    st.title("BriefBuzz : A Summarised News📰")
    image = Image.open('E:\\somaiya\\sem-6\\InNews-master\\InNews-master\\Meta\\logo.jpeg')

    col1, col2, col3 = st.columns([3, 5, 3])

    with col1:
        st.write("")

    with col2:
        st.image(image, use_column_width=True)

    with col3:
        st.write("")

    # Sidebar for category selection
    st.sidebar.title("Add link of your choice")
    url = st.sidebar.text_input("URL")
    summarize_button = st.sidebar.button("Summarize")

    if url.strip() != '' and summarize_button:
        summarize(url.strip())
    else:
        category = st.sidebar.selectbox('Category', ['Trending🔥 News', 'Favourite💙 Topics', 'Search🔍 Topic'])
        if category == 'Trending🔥 News':
            st.subheader("✅ Here are the Trending🔥 news for you")
            no_of_news = st.sidebar.slider('Number of News:', min_value=5, max_value=25, step=1)
            news_list = fetch_top_news()
            display_news(news_list, no_of_news)
        elif category == 'Favourite💙 Topics':
            chosen_topic = st.sidebar.selectbox("Choose your favourite Topic", ['WORLD', 'NATION', 'BUSINESS',
                                                                                'TECHNOLOGY', 'ENTERTAINMENT',
                                                                                'SPORTS', 'SCIENCE', 'HEALTH'])
            if chosen_topic:
                no_of_news = st.sidebar.slider('Number of News:', min_value=5, max_value=25, step=1)
                news_list = fetch_category_news(chosen_topic)
                if news_list:
                    st.subheader(f"✅ Here are the some {chosen_topic} News for you")
                    display_news(news_list, no_of_news)
                else:
                    st.error(f"No News found for {chosen_topic}")
        elif category == 'Search🔍 Topic':
            user_topic = st.sidebar.text_input("Enter your Topic🔍")
            if st.sidebar.button("Search") and user_topic.strip() != '':
                user_topic_pr = user_topic.replace(' ', '')
                st.write(f"Searching news for topic: {user_topic_pr}")  # Debug statement
                news_list = fetch_news_search_topic(topic=user_topic_pr)
                st.write(f"News list length: {len(news_list)}")  # Debug statement
                if news_list:
                    st.subheader(f"✅ Here are the some {user_topic.capitalize()} News for you")
                    no_of_news = st.sidebar.slider('Number of News:', min_value=5, max_value=15, step=1)
                    st.write(f"Number of news selected: {no_of_news}")  # Debug statement
                    display_news(news_list, no_of_news)
                else:
                    st.error(f"No News found for {user_topic}")


run()
