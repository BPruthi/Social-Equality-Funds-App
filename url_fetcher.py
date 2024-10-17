import os

from langchain_core.tools import Tool
from langchain_google_community import GoogleSearchAPIWrapper

from dotenv import load_dotenv

# Load environment 
load_dotenv()

os.environ["GOOGLE_CSE_ID"] = os.getenv("GOOGLE_API_SECRET")
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

search = GoogleSearchAPIWrapper()

def top5_results(query):
    return search.results(query, 5)


def find_top_search_results(company,keyword):

    tool = Tool(
        name="Google Search Snippets",
        description="Search Google for recent results.",
        func=top5_results,
    )
    final_query = f"{company} + {keyword} + pdf + report + latest"
    print("Final Query : ",final_query)

    data = tool.run(final_query)

    # print("\nSearch Results : \n",data)

    links = [item['link'] for item in data]

    return links if links else [item['Result'] for item in data if 'Result' in item]

# def search_top_5_urls(search_query):
#     tool.run("Obama's first name?")

