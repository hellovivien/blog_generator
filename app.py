import streamlit as st
from transformers import pipeline, set_seed
import random
import requests
import json
from fake_useragent import UserAgent
import people_also_ask
import time


def generate_blog():
    MAX_ARTICLES= 5
    task = st.sidebar.empty()
    task_details = st.sidebar.empty()
    prog_bar = st.sidebar.progress(0)
    subject = st.session_state.subject
    url = "https://suggestqueries.google.com/complete/search?output=chrome&hl=en&gl=us&q=" + subject
    ua = UserAgent()
    headers = {"user-agent": ua.chrome}
    response = requests.get(url, headers=headers, verify=False)
    suggestions = json.loads(response.text)
    related_words = suggestions[1]
    related_questions = []
    task.markdown("**Find article titles from google...**")
    for i, word in enumerate(related_words):
        if len(related_questions) < MAX_ARTICLES:
            prog_bar.progress(i/len(related_words))
            # st.markdown('**{}**'.format(word))
            questions = people_also_ask.get_related_questions(word, 5)
            for question in questions:
                if question not in related_questions:
                    st.success(question)
                    related_questions.append(question)
                    task_details.markdown('**{}** title(s)'.format(len(related_questions)))

    if len(related_questions) > 0:            
        task.markdown("**Generate articles with GPT2...**")
        st.markdown('<hr>', unsafe_allow_html=True)
        generator = pipeline('text-generation', model='gpt2')
        set_seed(42)
        st.session_state.articles = {}
        related_questions = related_questions[0:5]
        for i,question in enumerate(related_questions):
            prog_bar.progress(i/len(related_questions))
            article = generator(question, max_length=300, num_return_sequences=2)
            st.session_state.articles[question] = article[0]['generated_text'][len(question):]
            st.success('article {}: {}'.format(i+1, question))
            task_details.markdown('**{}** article(s)'.format(i+1))
        st.balloons()
        time.sleep(2)
        st.experimental_rerun()
    else:
        st.error('Your title is not good')



def get_article(question):
    st.markdown('## {}'.format(question))
    st.markdown(st.session_state.articles[question])  

if not 'articles' in st.session_state:
    with st.form('blog_generator'):
        subject = st.text_input('Title',key='subject',value='covid vaccine')
        st.form_submit_button('Generate your blog', on_click=generate_blog)           
else:
    for question in st.session_state.articles.keys():
        st.sidebar.button(question, key=str(random.random()), on_click=get_article, args=(question,))



