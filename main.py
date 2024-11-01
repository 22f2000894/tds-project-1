import requests
import pandas as pd
import os, time
from string import Template
# GitHub API endpoint and headers
API_URL = "https://api.github.com/graphql"
GITHUB_TOKEN = "github personal access token"  # Replace with your actual GitHub token
HEADERS = {"Authorization": f"Bearer {GITHUB_TOKEN}"}

# Query Parameters
CITY = "Hyderabad"
FOLLOWERS_MIN = 50
USER_COUNT = 5  # Adjust as needed; set to lower for testing
REPO_COUNT = 100  # Maximum repos per user per request

# GraphQL Queries
def get_users_query(user_cursor=None, repo_cursor=None, USER_COUNT=5, REPO_COUNT=100):
    user_cursor_query = f', after: "{user_cursor}"' if user_cursor else ""
    repo_cursor_query = f', after: "{repo_cursor}"' if repo_cursor else ""

    
    query_template = Template("""
      query {
        search(query: "location:Hyderabad followers:>50", type: USER, first: $USER_COUNT $user_cursor_query) {
          pageInfo {
            endCursor
            hasNextPage
          }
          edges {
            node {
              ... on User {
                login
                name
                company
                location
                email
                hireable: isHireable
                bio
                followers {
                  totalCount
                }
                following {
                  totalCount
                }
                createdAt
                repositories(first: $REPO_COUNT $repo_cursor_query, orderBy: {field: PUSHED_AT, direction: DESC}, privacy: PUBLIC) {
                  totalCount
                  pageInfo {
                    endCursor
                    hasNextPage
                  }
                  edges {
                    node {
                      name
                      createdAt
                      stargazers {
                        totalCount
                      }
                      watchers {
                        totalCount
                      }
                      language: primaryLanguage {
                        name
                      }
                      hasProjects: hasProjectsEnabled
                      hasWiki: hasWikiEnabled
                      licenseInfo {
                        key
                      }
                      visibility
                    }
                  }
                }
              }
            }
          }
        }
      }
    """)

    query = query_template.substitute(USER_COUNT=USER_COUNT, 
    user_cursor_query=user_cursor_query, 
    REPO_COUNT=REPO_COUNT, 
    repo_cursor_query=repo_cursor_query)
    return query

# fetch repositories for each  user and paginate after 100 repositories
def fetch_repositories(user_login, repo_cursor=None):
    repo_cursor_query = f', after: "{repo_cursor}"' if repo_cursor else ""

  # GraphQL query template
    repo_template = Template("""
        query{
          user(login: "$user_login") {
            repositories(first: 100 $repo_cursor_query ,orderBy: {field: PUSHED_AT, direction: DESC}, privacy: PUBLIC) {
              totalCount
              pageInfo {
                endCursor
                hasNextPage
              }
              edges {
                node {
                  name
                  createdAt
                  stargazers {
                    totalCount
                  }
                  watchers {
                    totalCount
                  }
                  language: primaryLanguage {
                    name
                  }
                  hasProjects: hasProjectsEnabled
                  hasWiki: hasWikiEnabled
                  licenseInfo {
                    key
                  }
                  visibility
                }
              }
            }
          }
        }
    """)
    repo_template = repo_template.substitute(user_login=user_login,
     repo_cursor_query=repo_cursor_query)
    return repo_template



# Function to make GraphQL requests
def run_query(query):
    time.sleep(1)
    response = requests.post(API_URL, json={"query": query}, headers=HEADERS)
    if response.status_code == 200:
        # print(response.json())
        return response.json()
    # else:
    #     raise Exception(f"Query failed to run: {response.status_code}\n{response.text}")
    elif response.status_code == 403:
      # Rate limit exceeded emplement for retry and wait for 65 seconds
        print("Rate limit exceeded. Waiting for 60 seconds...")
        time.sleep(65)
        response = requests.post(API_URL, json={"query": query}, headers=HEADERS)
        if response.status_code == 200:
            print("Request successful")
            return response.json()
        else:
            print("Request failed with status code:", response.status_code)
            print("Response content:", response.text)
            raise Exception("Rate limit exceeded. Try again later.")
    
    else:
        print("Failed request status:", response.status_code)
        print("Response content:", response.text)
        raise Exception(f"Query failed to run with status code {response.status_code}")
# Process and clean company names
def clean_company_name(company):
    if not company:
        return ""
    company = company.strip().upper()
    return company[1:] if company.startswith("@") else company

# Fetch data and paginate
users_data, repos_data = [], []
user_cursor = None
user_counter = 0
while True:
    user_counter += 1
    query = get_users_query(user_cursor,USER_COUNT=5, REPO_COUNT=100)
    data = run_query(query)
    search_data = data["data"]["search"]
    check_page = 0
    for user_edge in search_data["edges"]:
      check_page += 1
      public_repos_count = 0
      repos_count = 0
      user_node = user_edge["node"]

      if user_node != {}:
        # user_login = str(user_login)
        user_data_obj = {
            "login": user_node["login"] or "",
            "name": user_node["name"] or "",
            "company": clean_company_name(user_node.get("company")),
            "location": user_node.get("location") or "",
            "email": user_node.get("email") or "",
            "hireable": user_node["hireable"] or "",
            "bio": user_node.get("bio") or "",
            "public_repos": user_node["repositories"]['totalCount'],
            "followers": user_node["followers"]["totalCount"],
            "following": user_node["following"]["totalCount"],
            "created_at": user_node["createdAt"]
        }
        # users_data.append(user_data)
        user_login = user_data_obj["login"]
        print("fetching user_login:", user_login)
        # Paginate through repositories
        repo_cursor = None
        first_repo_page = True
        while True:
            if first_repo_page:
              repo_page = user_node["repositories"]
            for repo_edge in repo_page["edges"]:
                
                if repo_edge["node"]["visibility"] == "PUBLIC":
                    public_repos_count += 1
                    repo_node = repo_edge["node"]
                    repo_data_obj = {
                        "login": user_node["login"],
                        "full_name": repo_node["name"],
                        "created_at": repo_node["createdAt"],
                        "stargazers_count": repo_node["stargazers"]["totalCount"],
                        "watchers_count": repo_node["watchers"]["totalCount"],
                        "language": repo_node["language"]["name"] if repo_node["language"] else "",
                        "has_projects": repo_node["hasProjects"],
                        "has_wiki": repo_node["hasWiki"],
                        "license_name": repo_node["licenseInfo"]["key"] if repo_node["licenseInfo"] else ""
                    }
                    repos_data.append(repo_data_obj)
                    repos_count += 1

            # Check for more repos for this user
            if repo_page["pageInfo"]["hasNextPage"] and repos_count < 500:
                repo_cursor = repo_page["pageInfo"]["endCursor"]
                print("fetching next page of user_login:", user_login)
                if  user_login != "":
                  repo_next_query = fetch_repositories(user_login, repo_cursor)
                  repo_response = run_query(repo_next_query)
                  repo_page = repo_response["data"]["user"]["repositories"]
                  first_repo_page = False
                else:
                  break
            else:
                repos_count = 0
                break
        user_data_obj["public_repos"] = public_repos_count
        users_data.append(user_data_obj)
        
        print(user_counter,"next user --------------------------------")
      
    # Check if there are more users to paginate
    if search_data["pageInfo"]["hasNextPage"]:
        user_cursor = search_data["pageInfo"]["endCursor"]

    else:
        break
 
# Convert to DataFrames
users_df = pd.DataFrame(users_data)
repos_df = pd.DataFrame(repos_data)

# Export to CSV files
users_df.to_csv("users.csv", index=False)
repos_df.to_csv("repositories.csv", index=False)

