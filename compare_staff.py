import requests
import json
import pandas as pd

def get_works(name, page):
    
    #Given a name to search and a page number, return a json containing:
        # the id of the staff member
        # the full name of the staff member
        # a list of works that the staff member participated in with:
            #id
            #title
            #premiere date
            #the staff member's role
            
        
    
    query = '''
    query ($name: String, $page: Int) {
    	Staff(search: $name) {
    	  id
        name {
          userPreferred
        }
        staffMedia (page: $page, perPage: 25) {
          edges {
            node {
              id
              title {
                userPreferred
              }
              startDate {
                  year
                  month
                  day
                  }
            }
            staffRole
          }
        }
    	}
    }
    '''
    
    variables = {
        'name': name,
        'page': page
        }
    
    url = 'https://graphql.anilist.co'
    
    # Make the HTTP Api request
    response = requests.post(url, json={'query': query, 'variables': variables})
    return response.json()

def multipage(name):
    pages = []
    page = 1
    while True:
        res = get_works(name, page)
        if len(res['data']['Staff']['staffMedia']['edges']) < 25:
            if len(res['data']['Staff']['staffMedia']['edges']) > 0:
                pages.append(res)
            break
        pages.append(res)
        page = page + 1
    return pages
        

def process_jsons(pages):
    staff = pages[0]['data']['Staff']
    name = staff['name']['userPreferred']

    ids = set()
    ids_to_roles = {}
    ids_to_titles = {}
    
    for p in pages:
        works = p['data']['Staff']['staffMedia']['edges']
        for w in works:
            ids.add(w['node']['id'])
            if w['node']['id'] in ids_to_roles:
                ids_to_roles[w['node']['id']].append(w['staffRole'])
            else:
                ids_to_roles[w['node']['id']] = [w['staffRole']]
            ids_to_titles[w['node']['id']] = w['node']['title']['userPreferred']
            
    return name, ids, ids_to_roles, ids_to_titles

def comp_staff(p1, p2):
    
    pages1 = multipage(p1)
    n1, ids1, roles1, titles1 = process_jsons(pages1)
    #print(n1, ids1)
    pages2 = multipage(p2)
    n2, ids2, roles2, titles2 = process_jsons(pages2)
    #print(n2, ids2)
    
    shared = ids1.intersection(ids2)
    df = pd.DataFrame(columns = [n1, n2])
    for s in shared:
        df.loc[titles1[s]] = [', '.join(roles1[s]), ', '.join(roles2[s])]
    print(df)
    return df

if __name__ == '__main__':
    comp_staff("Miyazaki", "Kanada")
    # res = get_works("Kubo", 3)
    # staff = res['data']['Staff']
    # name = staff['name']['userPreferred']
    # works = staff['staffMedia']['edges']
    # ids = set()
    # ids_to_roles = {}
    # ids_to_titles = {}
    # for w in works:
    #     ids.add(w['node']['id'])
    #     if w['node']['id'] in ids_to_roles:
    #         ids_to_roles[w['node']['id']].append(w['staffRole'])
    #     else:
    #         ids_to_roles[w['node']['id']] = [w['staffRole']]
    #     ids_to_titles[w['node']['id']] = w['node']['title']['userPreferred']
    #print(json.dumps(res, indent=2))