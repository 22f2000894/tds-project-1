# tds-project-1

This is Tools For Data Science Project 1 in BS IN DATA SCIENCE AND  APPLICATIONS

<!-- README.md must begin with 3 bullet points. Each bullet must be one sentence no more than 50 words.

An explanation of how you scraped the data
The most interesting and surprising fact you found after analyzing the the data
An actionable recommendation for developers based on your analysis -->

- Scraped data from GitHub: Using GitHub's GraphQL API to fetch data about GitHub users located in Hyderabad with more than 50 followers. Each user most recently pushed to a repository up to 500 repositories. I am using pagination to fetch user first 5 users and each user has first up to 100 repositories.If repositories greater than 100, pagination is used to fetch up to 500 repositories. Using pandas to convert to DataFrames and then csv files. `users.csv` contains user details. `repositories.csv` contains repository details for each user.
query to scrap data from GitHub given location Hyderabad and followers more than 50
```graphql
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
```
and fetch repositories for each user
```graphql
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
```
- Data cleaned and structured: Cleaned and structured data to use in the project.
- Generated README.md: Generated README.md file for the project
