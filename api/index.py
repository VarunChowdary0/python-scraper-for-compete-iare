from flask import Flask, request, jsonify
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests
from warnings import filterwarnings

filterwarnings('ignore')

lc_fakes = []

class LeetcodeScraper:
    def __init__(self):
        self.base_url = 'https://leetcode.com/graphql'

    def scrape_user_profile(self, username):
        output = {
                    "name": None,
                    "problemsSolved": {
                        "All": -1,
                        "Easy": -1,
                        "Hard": -1,
                        "Medium": -1
                    },
                    "username": username
                    }
        
        session = requests.Session()

        def scrape_problems_solved():
            json_data = {
                'query': '''
                    query userProblemsSolved($username: String!) {
                        matchedUser(username: $username) {
                            username
                            profile {
                                realName
                            }
                            submitStatsGlobal {
                                acSubmissionNum {
                                    difficulty
                                    count
                                }
                            }
                        }
                    }
                ''',
                'variables': {'username': username},
                'operationName': 'userProblemsSolved',
            }

            try:
                response = session.post(self.base_url, json=json_data, stream=True, verify=False)
                
                if response.status_code == 200:
                    data = response.json().get('data', {}).get('matchedUser', {})
                    output['username'] = data.get('username')
                    output['name'] = data.get('profile', {}).get('realName')
                    problems_solved_data = data.get('submitStatsGlobal', {}).get('acSubmissionNum', [])
                    output['problemsSolved'] = {entry['difficulty']: entry['count'] for entry in problems_solved_data}
                    # print(f"Fetched user data: {output}")
                else:
                    print(f"Failed to fetch data, status code: {response.status_code}")
            except Exception as e:
                print(f'Error scraping LeetCode data for username {username}: {e}')
                lc_fakes.append("https://leetcode.com/u/"+username)

        scrape_problems_solved()

        return output

cc_falied = set()


class Scrapper():
    def __init__(self, url) -> None:
        headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Referer': 'https://google.com'
            }
        self.url = url
        session = requests.Session()
        self.response = session.get(self.url,headers=headers)

    def eei(self):
        # print("Scraping URL:", self.url)
        # print("Response Status:", self.response.status_code)
        soup = BeautifulSoup(self.response.content, 'html.parser') 
        return soup.prettify()
    
    def get_res(self):
        soup = BeautifulSoup(self.response.content, 'html.parser')
        if self.response.status_code == 200:
            title = soup.title.string if soup.title else "No Title Found"
            return jsonify({"title": title})
        else:
            return jsonify({"error": "Error fetching the URL"}), 400
    
    def get_geekForGeeks(self):
        if self.response.status_code == 200:
            soup = BeautifulSoup(self.response.content, 'html.parser')
            rank = soup.find("span", class_="educationDetails_head_left_userRankContainer--text__wt81s")
            if rank:
                rank = rank.b

            MyDict = {
                "username": "",
                "Rank": int(rank.text.strip('Rank')) if rank and rank.text.strip('Rank').isdigit() else -1,
                "score": -1,
                "problems_solved": -1,
                "contest_rating": -1,
                "college": None
            }

            scores = soup.find_all('div', class_="scoreCard_head_left--score__oSi_x")
            if scores:
                
                MyDict = {
                    "username": "",
                    "Rank": int(rank.text.strip('Rank')) if rank and rank.text.strip('Rank').isdigit() else -1,
                    "score": 0,
                    "problems_solved": 0,
                    "contest_rating": 0,
                    "college": None
                }
                # Check if the score text can be converted to an integer
                print(scores[0].text)
                if scores[0].text == '__':
                    MyDict["score"] = 0
                else:
                    MyDict["score"] = int(scores[0].text.strip()) if len(scores) > 0 and scores[0].text.strip().isdigit() else -1
                MyDict["problems_solved"] = int(scores[1].text.strip()) if len(scores) > 1 and scores[1].text.strip().isdigit() else -1
                # For contest_rating, check if it is not "__" or other invalid values
                contest_rating_text = scores[2].text.strip() if len(scores) > 2 else None
                MyDict["contest_rating"] = int(contest_rating_text) if contest_rating_text and contest_rating_text.isdigit() else -1

            college_res = soup.find('div', class_="educationDetails_head_left--text__tgi9I")
            MyDict['college'] = college_res.text.strip() if college_res else None

            username_res = soup.find('div', class_="profilePicSection_head_userHandle__oOfFy")
            MyDict['username'] = username_res.text.strip() if username_res else ""

            if not MyDict['username']:
                # Set all values to -1 if the username does not exist
                MyDict = {key: -1 if isinstance(value, int) else None for key, value in MyDict.items()}
                MyDict['username'] = ""

            return MyDict
        else:
            return {"error": "Error fetching the URL"}

            
    def get_CodeChef(self, username):
        if self.response.status_code == 429:
            print('Too many Requests',username)
            cc_falied.add(username)
            return {}
        if self.response.status_code == 400:
            return {"error": "Error fetching the CodeChef URL", "url": self.url,"status":self.response.status_code}
        
        soup = BeautifulSoup(self.response.content, 'html.parser')
        myDict = {
            "problems-Solved": 0,
            "contests": 0,
            "name": None,
            "username": ""
        }

        # Helper function to extract numeric values safely
        def extract_numeric_value(text, prefix):
            if text.startswith(prefix):
                value = text[len(prefix):].strip()
                return int(value) if value.isdigit() else 0
            return -1

        # Extracting problems solved and contests
        res = soup.find("section", class_="rating-data-section problems-solved")
        if res:
            res2 = res.find_all("h3")
            for h3_tag in res2:
                text = h3_tag.text.strip()
                myDict['problems-Solved'] = extract_numeric_value(text, "Total Problems Solved:") if "Total Problems Solved" in text else myDict['problems-Solved']
                myDict['contests'] = extract_numeric_value(text, "Contests (") if "Contests" in text else myDict['contests']

        # Extracting the name
        res_name = soup.find('h1', class_="h2-style")
        myDict['name'] = res_name.text.strip() if res_name else None

        # Extracting the username
        res_user = soup.find('ul', class_="side-nav")
        if res_user:
            for li in res_user.find_all('li'):
                if "Username:" in li.text:
                    extracted_username = li.text.split("Username:")[-1].strip("7\u2605").strip()
                    myDict['username'] = extracted_username if extracted_username else ""

        # Fallback to the provided username if the extracted one is empty
        myDict['username'] = myDict['username'] or username

        # Validate the username and set fields to -1 if not found
        if not myDict['username']:
            myDict = {key: -1 if isinstance(value, int) else None for key, value in myDict.items()}
            myDict['username'] = ""

        return myDict


    def get_HackerRank(self):
        # print(self.url)
        if self.response.status_code == 200:
            soup = BeautifulSoup(self.response.content,'html.parser')
            res = soup.find_all('div',class_='hacker-badge')
            myDct = {
                        "badges":{
                            "oneStarBadge": 0,
                            "twoStarBadge": 0,
                            "threeStarBadge": 0,
                            "fourStarBadge": 0,
                            "fiveStarBadge": 0
                        },
                        "certificates":{
                            "basic" : 0,
                            "intermediate":0,
                            "advanced" : 0
                        }
                    }
            for i in range(len(res)):
                re0 = res[i].find('g',class_="star-section")
                res2 = (re0.find_all('svg',class_="badge-star"))
                # myDct['badges'][f"badge-{i+1}"] = len(res2)
                if len(res2) == 1:
                    myDct['badges']['oneStarBadge'] += 1
                if len(res2) == 2:
                    myDct['badges']['twoStarBadge'] += 1
                if len(res2) == 3:
                    myDct['badges']['threeStarBadge'] += 1
                if len(res2) == 4:
                    myDct['badges']['fourStarBadge'] += 1
                if len(res2) == 5:
                    myDct['badges']['fiveStarBadge'] += 1

            res = soup.find_all('a',class_="certificate-link hacker-certificate")
            # print(len(res))
            for i in range(len(res)):
                Basic = res[i].find_all("h2")
                # print(Basic)
                for j in Basic:
                    j = (str(j.text).split(" "))
                    if "(Basic)" in j:
                        myDct['certificates']['basic'] += 1
                    elif "(Intermediate)" in j:
                        myDct['certificates']['intermediate'] += 1
                    elif "(Advanced)" in j:
                        myDct['certificates']['advanced'] += 1
            name = soup.find('h1',class_="hr-heading-02 profile-title ellipsis")
            myDct['name'] = (name and name.text) or None
            userName = soup.find('p',class_="profile-username-heading hr-body-01 hr-m-t-0.25")
            # print(userName)
            if userName:
                myDct['username'] = userName.text.strip("@")
            return myDct

app = Flask("MyApp")
CORS(app)

@app.route('/empty_cc_failed', methods=['POST','GET'])
def clear_Aa():
    cc_falied = set()
    print("Cleared")
    return "OK"


@app.route("/", methods=['POST', 'GET'])
def default_page():
    # scrap = Scrapper(url="https://www.geeksforgeeks.org/user/saivarunchowdarnlth/")
    print(cc_falied)
    return list(cc_falied)

@app.route("/test", methods=['POST', 'GET'])
def test():
    if request.method == 'POST':
        data = request.get_json()
        a = data.get('a')
        b = data.get('b')
        sum_result = a + b
        return jsonify({"sum": sum_result})
    else:
        a = int(request.args.get('a'))
        b = int(request.args.get('b'))
        sum_result = a + b
        return jsonify({"sum": sum_result})
    
@app.route("/test_url_gfg",methods=['POST','GET'])
def test2():
    if request.method == 'POST':
        username = request.get_json()['username']
    else:
        username = request.args.get("username").strip()    
    scrp = Scrapper("https://www.geeksforgeeks.org/user/"+username)
    print(scrp.get_geekForGeeks())
    return scrp.get_geekForGeeks() or "Error Occured"

@app.route("/test_url_cc",methods=['POST','GET'])
def test3():
    if request.method == 'POST':
        username = request.get_json()['username']
    else:
        username = request.args.get("username").strip()
    scrp = Scrapper("https://www.codechef.com/users/"+username)
    resp = scrp.get_CodeChef(username)
    if username == 'varun9392':
        print(resp,"------------------------- \n\n\n ------- 009o",username)
    # print(resp)
    return jsonify(resp)

@app.route("/test_url_lc",methods=['POST','GET'])
def test4():
    if request.method == 'POST':
        username = request.get_json()['username']
    else:
        username = request.args.get("username").strip()
    leet  =LeetcodeScraper()
    res = leet.scrape_user_profile(username)
    print(dict(res))
    return jsonify(res) or "Error Occured"

@app.route("/test_url_hrc",methods=['POST','GET'])
def test5():
    if request.method == 'POST':
        username = request.get_json()['username']
    else:
        username = request.args.get("username").strip()
    scrap = Scrapper('https://www.hackerrank.com/profile/'+username)
    res = scrap.get_HackerRank()
    print(res)
    return jsonify(res) or "Error Occured"


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, port=10001, host="0.0.0.0")
