#!/Users/mac/.conda/envs/dbSequential/bin/python
"""
    Case Study
    Use the Guardian Media Group API.
Q1. Extract information about Justin Trudeau.
Q2. Count how many articles about Justin Trudeau have been posted since 01.01.2018 until today:
    The output should consist of two columns:
    „Date“ and „No. of articles“ 2018-01-01 3 2018-01-02 4 2018-01-03 2
Q3. Calculate the average of all days for the above-mentioned period from “No. of articles”.
Q4. In which section are most articles written?
Q5. Show the evolution of the "No. of articles" over time for the above period.
Q6. Are there any unusual events in the time series under investigation?
Q7. If so, show these. Why are these unusual? (Define for yourself what you want to show by ordinary or unusual).
Q8. Based on question one. Show the cause of the unusual event.

Create a daily automated job that updates question 5 daily and creates an output that could be sent to recipients who have not seen the data before.
"""

import json
import requests
import pathlib
import os
from datetime import datetime
import matplotlib.pyplot as plt


class JustinTrudeau_InfoClass(object):
    '''
        JustinTrudeau_InfoClass is the class enclosing the entire logic.
        It is instantiated in execute.py.
    '''

    key = open("/Users/mac/PycharmProjects/dbSequential/caseStudy/key.txt").read().strip()
    endpoint = 'http://content.guardianapis.com/'

    params_q1 = {
        'q': '"Justin Trudeau"',
        'format': 'json',
        'order-by': "newest",
        'show-fields': 'all',
        'show-tags': 'all',
        'show-section': True,
        'show-elements': 'all',
        'page-size': 50,
        'api-key': key
    }

    page_current = 1
    pages = 1

    def get_information(self, question, file_path):
        '''
            query the API for information regarding Justin Trudeau
            saving the information in different json files
        '''
        endpoint = self.endpoint + '/search'
        while self.page_current <= self.pages:
            print("Page ", self.page_current)
            self.params_q1['page'] = self.page_current
            resp = requests.get(endpoint, self.params_q1)
            data = resp.json()

            with open(file_path + '/Q'+str(question)+'/page_' + str(self.page_current) + '.json', 'w') as f:
                print("Write page", self.page_current)

                f.write(json.dumps(data, indent=2))

            self.page_current += 1
            self.pages = data['response']['pages']

        return

    def post_process_info(self, directory):
        '''
            rename the files that store information about Justin Trudeau with the dates of the first and last
            publications within the particular file
        '''
        for filename in self.get_files(directory):
                with open(filename) as f:
                    d = json.load(f)
                    try:
                        elem_start = d["response"]["results"][0]["webPublicationDate"]
                        startdate = elem_start[:10]
                        elem_end = d["response"]["results"][-1]["webPublicationDate"]
                        enddate = elem_end[:10]
                    except IndexError:
                        print('Error regarding number of elements parsed in the json.')
                    os.rename(filename, directory + '/' + str(enddate)+'_'+str(startdate)+'.json')

    def get_files(self, directory):
        '''
            list of file getter within a directory
        '''
        list_of_files = []
        current_directory = pathlib.Path('./' + directory)
        for currentFile in current_directory.iterdir():
            str_currentfile = str(currentFile)
            if str_currentfile.endswith('.json'):
                list_of_files.append(str_currentfile)

        return list_of_files

    def info_since_date(self, date, directory_from, directory_to):
        '''
            filter the information about Justin Trudeau and store only the articles since 2018-01-01
        '''
        since_date_results = []
        date_y = int(date.split('-')[0])
        for filename in self.get_files(directory_from):
            startdate = str(filename).split('-')[0].split('/')[2]
            #print(startdate)
            enddate = str(filename).split('_')[1].split('-')[0]
            #print(enddate)
            if int(startdate) >= date_y or int(enddate) >= date_y:
                with open(filename) as f:
                    #print(filename)
                    d = json.load(f)
                    since_date_results.extend(d['response']['results'])
            else:
                continue

        with open(directory_to+'/information_since_'+date+'.json', 'w') as f:
            f.write(json.dumps(since_date_results, indent=2))
        return f.name

    def nr_of_articles_daily(self, file_from, file_to, date_since):
        '''
            count the number of articles published about Justin Trudeau since 2018-01-01
            for days when there was no article found - no entry is created
        '''
        with open(file_from) as f:
            all_since = json.load(f)
            all_article_dates = []
            for i in range(len(all_since)):
                try:
                    t = all_since[i]["type"]
                    if str(t) == 'article':
                        article_date = all_since[i]["webPublicationDate"][:10]
                        if str(article_date).split('-')[0] >= '2018':
                            all_article_dates.append(article_date)

                        else:
                            continue
                except IndexError:
                    print(IndexError)

        a = []
        for date in all_article_dates:
            a.append([date, all_article_dates.count(date)])
            a.sort()

        s = []
        for i in a:
            if i not in s:
                s.append(i)
        with open(file_to + '/article_count_by_since_' + date_since + '.txt', 'w') as f:
            f.write('Date         ' + 'No. of articles' + '\n')
            for match in s:
                f.write(str(match[0]) + '   ' + str(match[1]) + '\n')

        return s

    def get_average_of_no_articles(self, date, articles, file_to):
        '''
            compute the average of the number of articles since 2018-01-01
        '''
        start_date = datetime.strptime(date, '%Y-%m-%d')
        now = datetime.now()
        days = (now - start_date).days + 1
        sum_art = 0
        for article in articles:
           sum_art = sum_art + article[1]

        with open(file_to + '/average_articles_since' + date + '.txt', 'w') as f:

            f.write('Nr. of days since ' + date + ': ' + str(days) + '\n')
            f.write('Nr. of articles since ' + date + ': ' + str(sum_art) + '\n')
            f.write('Average of articles since ' + date + ': ' + str(round(sum_art / days, 2)) + '\n')

        return

    def get_most_popular_section(self, directory_from, file_to):
        '''
            determine the most popular section
        '''
        arr_of_sections = []
        for filename in self.get_files(directory_from):
                with open(filename) as f:
                    d = json.load(f)
                    for i in range(50):
                        try:
                            section_id = d["response"]["results"][i]["sectionId"]
                            arr_of_sections.append(section_id)
                        except IndexError:
                            print('Error regarding number of elements parsed in the json.')
        a = []
        for section in arr_of_sections:
            a.append([section, arr_of_sections.count(section)])

        s = []
        for i in a:
            if i not in s:
                s.append(i)
        s.sort()
        with open(file_to + '/most_popular_section.txt', 'w') as f:

            f.write('Section: ' + s[-1][0] + '\n')
            f.write('Nr. of occurrences: ' + str(s[-1][1]) + '\n')
        return

    def daily_update_evolution(self, articles):
        '''
            request every day the new published articles
            cron job was set up by using Jenkins
        '''
        now = datetime.now()
        now = now.strftime('%Y-%m-%d')
        endpoint = self.endpoint + '/search'
        self.params_q1['from-date'] = now
        self.params_q1['to-date'] = now
        resp = requests.get(endpoint, self.params_q1)
        new_data = resp.json()
        if int(new_data['response']["total"]) == 0:
            articles = articles
        else:
            c=0
            for i in range(len(new_data)):
                t = new_data["response"]["results"][i]["type"]
                if str(t) == 'article':
                    c += 1
                else:
                    continue
            if c > 0:
                articles.append([now, c])
        return articles

    def plot_nr_of_articles_evolution(self, file_to, date, array_nr_of_articles):
        '''
            create plots to analyse the evolution of the number of articles since 2018-01-01
        '''
        now = datetime.now()
        now = now.strftime('%Y-%m-%d')

        y_axis = []
        x_axis = []
        for data in array_nr_of_articles:
            y_axis.append(data[0])
            x_axis.append(data[1])
        #print(y_axis)
        #print(x_axis)
        fig, ax = plt.subplots()
        #ax.scatter(y_axis, x_axis, marker='o')
        ax.plot(y_axis, x_axis)
        for index, label in enumerate(ax.xaxis.get_ticklabels()):
            if index % 10 != 0:
                label.set_visible(False)

        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(5)

        plt.xticks(rotation=90)

        plt.xlabel('Date since ' + date + ' until today')
        plt.ylabel('Number of articles')

        plt.title('Evolution of published articles including information about Justin Trudeau')
        #plt.savefig(file_to+'/evolution_plot_since_'+date+'_until_'+ now +'.png')
        plt.savefig(file_to+'/evolution_lineplot_since_'+date+'_until_'+ now +'.png')

        return

    def unusual_events_case(self, articles, directory_from):
        articles
        return

    '''
       the script is run every day within a cron job on Jenkins - see printscreen in folder Q5
    '''
directory_name = '/Users/mac/PycharmProjects/dbSequential/caseStudy/JustinTrudeau'
get_info = JustinTrudeau_InfoClass()
date = '2018-01-01'
filename = directory_name + '/Q2/information_since_'+date+'.json'
articles = get_info.nr_of_articles_daily(filename, directory_name+'/Q2', date)
articles = get_info.daily_update_evolution(articles)
get_info.plot_nr_of_articles_evolution(directory_name+'/Q5', date, articles)





