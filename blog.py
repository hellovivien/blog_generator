from app import Blog
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
import streamlit as st

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
client = AsyncIOMotorClient("adresse de ta base mongodb: https://www.mongodb.com/try")
engine = AIOEngine(motor_client=client, database="blog")

def draw_line(st=st):
    st.write('<hr>', unsafe_allow_html=True)


async def main():
    with open('style.css') as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)       
    blogs = await engine.find(Blog, sort=Blog.created_at.desc())
    current_blog = st.sidebar.selectbox('Blogs', blogs, format_func=lambda x: x.title)
    draw_line(st.sidebar)
    for article in current_blog.articles:
        if st.sidebar.button(article.title, key=article.content[0:10]):
            st.markdown('## {}'.format(article.title))
            draw_line()
            st.markdown(article.content)    



if __name__ == "__main__":
    loop.run_until_complete(main())    
