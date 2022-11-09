import requests
import json
import pandas as pd
import time

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
        staffMedia (page: $page, perPage: 25, sort:START_DATE) {
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

    #get all pages for a staff member

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

    #parse results returned by API

    staff = pages[0]['data']['Staff']
    name = staff['name']['userPreferred']

    ids = set()
    ids_to_roles = {}
    ids_to_titles = {}
    ids_to_years = {}
    
    for p in pages:
        works = p['data']['Staff']['staffMedia']['edges']
        for w in works:
            ids.add(w['node']['id'])
            if w['node']['id'] in ids_to_roles:
                ids_to_roles[w['node']['id']].append(w['staffRole'])
            else:
                ids_to_roles[w['node']['id']] = [w['staffRole']]
            ids_to_titles[w['node']['id']] = w['node']['title']['userPreferred']
            ids_to_years[w['node']['id']] = w['node']['startDate']['year']
            
    return name, ids, ids_to_roles, ids_to_titles, ids_to_years
        

def comp_staff(p1, p2):

    # No longer in use. Compare two staff members.
    
    pages1 = multipage(p1)
    n1, ids1, roles1, titles1, years1 = process_jsons(pages1)
    #print(n1, ids1)
    pages2 = multipage(p2)
    n2, ids2, roles2, titles2, years2 = process_jsons(pages2)
    #print(n2, ids2)
    
    shared = ids1.intersection(ids2)
    df = pd.DataFrame(columns = ['year', n1, n2])
    for s in shared:
        df.loc[titles1[s]] = [years1[s], ', '.join(roles1[s]), ', '.join(roles2[s])]
    print(df.sort_values(by=['year']))
    return df.sort_values(by=['year'])


class Comparer:

    #Class for comparing staff

    def __init__(self, names):
        self.names = [] #list of names
        self.ids = [] # list of sets containing AniList ids of everything a staff member worked on
        self.table = None # table for showing comparison
        self.rolesdicts = [] # list of dictionaries going from AniList ids of works to role(s) of staff member on that work.
        self.titlesdicts = [] # list of dicionaries going from AniList ids of works to titles
        self.yearsdicts = [] # list of dictionaries going from AniList ids to release year
        self.shared = set() # set of AniList ids that are shared by at least two staff members in the comparison
        #NOTE: names, ids, rolesdicts, titlesdicts, and yearsdicts are in the same order

        self.comp_multi(names)
        
    def comp_multi(self, names):
        
        #compare multiple staff members
        
        for n in names:
            pages = multipage(n)
            nm, ids, roles, titles, years = process_jsons(pages)
            
            self.names.append(nm)
            self.add_set(ids)
            #idslist.append(ids)
            
            self.rolesdicts.append(roles)
            self.titlesdicts.append(titles)
            self.yearsdicts.append(years)
            
        self.make_table()
    
    def make_table(self):

        # make the table

        df = pd.DataFrame(columns = ['year']+self.names)
        for s in self.shared:
            
            for td in self.titlesdicts:
                if s in td:
                    tit = td[s]
                    break
            
            for yd in self.yearsdicts:
                if s in yd:
                    yr = yd[s]
                    break
            
            staff_roles = []
            for rd in self.rolesdicts:
                if s in rd:
                    staff_roles.append(rd[s])
                else:
                    staff_roles.append("")
                    
            df.loc[tit] = [yr] + [', '.join(s) for s in staff_roles]
        print(df.sort_values(by=['year']))
        self.table = df.sort_values(by=['year'])
    
    def add_set(self, newset):

        # recalculate the shared set and add the new set of ids

        for s in self.ids:
            self.shared|=s&newset
        self.ids.append(newset)

if __name__ == '__main__':
    print(1)
    c = Comparer(["Miyazaki", "Kanada"])
