from caseStudy.FormatDir import FormatDirectoryHierarchy
from caseStudy import JustinTrudeau_InfoClass

'''
    execution script
    triggers the entire logic, the functions are dependent on each other
'''
###create directory hierarchy
#create_dir = FormatDirectoryHierarchy()
directory_name = 'JustinTrudeau'
#questions = 8
#create_dir.create_directory(directory_name, questions)
###

###get all information regarding JustinTrudeau and postprocess files
get_info = JustinTrudeau_InfoClass()
#question = 1
#get_info.get_information(question, directory_name)
#get_info.post_process_info(directory_name+'/Q1')
###

###get number of articles since 2018-01-01
date='2018-01-01'
filename = get_info.info_since_date(date, directory_name+'/Q1', directory_name+'/Q2')
articles = get_info.nr_of_articles_daily(filename, directory_name+'/Q2', date)
###

###get average number of articles since 2018-01-01
get_info.get_average_of_no_articles(date, articles, directory_name+'/Q3')
###

###get most pupular section
get_info.get_most_popular_section(directory_name+'/Q1', directory_name+'/Q4')
###

###evolution analysis
articles = get_info.daily_update_evolution(articles)
get_info.plot_nr_of_articles_evolution(directory_name+'/Q5', date, articles)
###

get_info.get_average_per_month(articles)
