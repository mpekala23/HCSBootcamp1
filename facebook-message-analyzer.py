
# coding: utf-8

# # Facebook Message Analyzer

# <b> Current Features For a Given Chat: </b>
# <ul>
#     <li> Number of Messages Sent </li>
#     <li> Messages Sent Over Time </li>
#     <li> Average Word Count </li>
# </ul>

# In[5]:


import os
import json
import numpy as np
import pylab as pl
import datetime

CURRENT_DIRECTORY = os.getcwd()
NUMBER_TO_ANALYZE = 5000
MESSAGE_THRESHOLD = 10
MESSAGE_BOUND = 1000


# In[6]:


def get_json_data(chat):
    try:
        json_location = CURRENT_DIRECTORY + "/messages/" + chat + "/message.json"
        with open(json_location) as json_file:
            json_data = json.load(json_file)
            return json_data
    except IOError:
        pass # some things the directory aren't messages (DS_Store, stickers_used, etc.)


# In[7]:


chats = os.listdir(CURRENT_DIRECTORY + "/messages/")[:NUMBER_TO_ANALYZE]
sorted_chats = []
final_data_messages = {}
final_data_times = {}
final_data_words = {}
# Average response time if a message includes a given word
final_word_to_average = {}
# Number of times a word must have been sent to be included in word statistics
word_cutoff = 6
invalid_message_count = 0
# Average response time to a given person
final_person_to_average = {}


# In[9]:


print('Analyzing ' + str(min(NUMBER_TO_ANALYZE, len(chats))) + ' chats...')

for chat in chats:
    url = chat + '/message.json'
    json_data = get_json_data(chat)
    print(chat)
    if json_data != None:
        messages = json_data["messages"]
        if len(messages) >= MESSAGE_THRESHOLD and len(messages) <= MESSAGE_BOUND:
            sorted_chats.append((len(messages), chat, messages))

sorted_chats.sort(reverse=True)

print('Finished processing chats...')


# In[10]:

for i, (messages, chat, messages) in enumerate(sorted_chats):
    number_messages = {}
    person_to_times = {}
    number_words = {}
    # Number of times a word was sent
    word_to_num = {}
    # Total of response time for messages including word
    word_to_time = {}
    # Average response time if a message includes word
    word_to_average = {}
    # Keep track of data about last words sent in relation to response time
    prev_time = None
    prev_words = []
    # Number of time a person sent a message (and the next message was sent by someone else)
    person_to_num = {}
    # Total of response time for messages sent by certain person
    person_to_response_time = {}
    # Average time to respond to a certain person
    person_to_average = {}
    prev_person_time = None
    prev_person = None

    print(str(i) + " - " + str(len(messages)) + " messages - " + str(chat))

    for message in messages[::-1]:
        try:
            name = message["sender_name"]
            time = message["timestamp_ms"]

            message_content = message["content"]

            # Code to caculate the average time for response to certain words
            if prev_time:
                for word in prev_words:
                    word_to_num[word.lower()] = word_to_num.get(word.lower(),0) + 1
                    word_to_time[word.lower()] = word_to_time.get(word.lower(),0) + time-prev_time
            prev_time = time
            prev_words = message_content.split()

            if prev_person_time and name != prev_person:
                person_to_num[name] = person_to_num.get(name,0) + 1
                person_to_response_time[name] = person_to_response_time.get(prev_person,0) + time-prev_person_time
                prev_person_time = time
            elif name != prev_person:
                prev_person_time = time

            number_messages[name] = number_messages.get(name, 0)
            number_messages[name] += 1

            person_to_times[name] = person_to_times.get(name, [])
            person_to_times[name].append(datetime.datetime.fromtimestamp(time/1000.0))

            number_words[name] = number_words.get(name, [])
            number_words[name].append(len(message_content.split()))
        except KeyError:
            # happens for special cases like users who deactivated, unfriended, blocked
            invalid_message_count += 1
    # Calculate average response time for every word in the chat
    for word in word_to_num:
        if word_to_num[word] >= word_cutoff:
            word_to_average[word] = word_to_time[word]/word_to_num[word]

    for person in person_to_num:
        person_to_average[person] = person_to_response_time[person]/person_to_num[person]/1000/60

    final_data_messages[i] = number_messages
    final_data_times[i] = person_to_times
    final_data_words[i] = number_words
    final_word_to_average[i] = word_to_average
    final_person_to_average[i] = person_to_average

print('Found ' + str(invalid_message_count) + ' invalid messages...')
print('Found ' + str(len(sorted_chats)) + ' chats with ' + str(MESSAGE_THRESHOLD) + ' messages or more')


# In[12]:


def plot_num_messages(chat_number):
    plotted_data = final_data_messages[chat_number]
    X = np.arange(len(plotted_data))
    pl.bar(X, list(plotted_data.values()), align='center', width=0.5, color = 'r', bottom = 0.3)
    pl.xticks(X, plotted_data.keys(), rotation = 90)
    pl.title('Number of Messages Sent')
    pl.tight_layout()
    pl.show()

def plot_histogram_time(chat_number):
    person_to_times = final_data_times[chat_number]
    pl.xlabel('Time')
    pl.ylabel('Number of Messages')
    pl.title('# of Messages Over Time')
    colors = ['b', 'r', 'c', 'm', 'y', 'k', 'w', 'g']
    for i , person in enumerate(person_to_times):
        plotted_data = person_to_times[person]
        pl.hist(plotted_data, 100, alpha=0.3, label=person, facecolor=colors[i % len(colors)])
    pl.legend()
    pl.xticks(rotation=90)
    pl.tight_layout()
    pl.show()

def plot_histogram_words(chat_number):
    temp = {}
    for person in final_data_words[chat_number]:
        temp[person] = np.average(final_data_words[chat_number][person])
    plotted_data = temp
    X = np.arange(len(plotted_data))
    pl.bar(X, list(plotted_data.values()), align='center', width=0.5, color = 'r', bottom = 0.5)
    pl.xticks(X, plotted_data.keys(), rotation = 90)
    pl.title('Average Word Count')
    pl.tight_layout()
    pl.show()

def plot_word_response_time(chat_number):
    # Turn our final_word_to_average dict into a series of plottable lists
    sort_vals = sorted((value, key) for (key,value) in final_word_to_average[chat_number].items())
    quickest = sort_vals[:10]
    quickest_vals = [(pair[0]/1000)/60 for pair in quickest]
    quickest_keys = [pair[1] for pair in quickest]
    slowest = sort_vals[-10:][::-1]
    slowest_vals = [(pair[0]/1000)/60 for pair in slowest]
    slowest_keys = [pair[1] for pair in slowest]
    # Plot quickest response time words
    X = np.arange(len(quickest))
    pl.bar(X, quickest_vals, align='center', width=0.5, color='g', bottom=0.3)
    pl.xticks(X, quickest_keys, rotation=90)
    pl.title('Response Time if Word ___ Included in Message (quickest)')
    pl.tight_layout()
    pl.xlabel("Word")
    pl.ylabel("Response Time (mins)")
    pl.show()
    # Plot slowest response time words
    X = np.arange(len(slowest))
    pl.bar(X, slowest_vals, align='center', width=0.5, color='b', bottom=0.3)
    pl.xticks(X, slowest_keys, rotation=90)
    pl.title('Response Time if Word ___ Included in Message (slowest)')
    pl.tight_layout()
    pl.xlabel("Word")
    pl.ylabel("Response Time (mins)")
    pl.show()

def plot_person_response_time(chat_number):
    data = final_person_to_average[chat_number]
    X = np.arange(len(data))
    pl.bar(X, list(data.values()), align='center', width=0.5, color='y', bottom=0.3)
    pl.xticks(X, list(data.keys()), rotation=90)
    pl.title('Response time based on who texts')
    pl.tight_layout()
    pl.xlabel("Person")
    pl.ylabel("Response Time (mins)")
    pl.show()

def plot(chat_number):
    plot_num_messages(chat_number)
    plot_histogram_time(chat_number)
    plot_histogram_words(chat_number)
    plot_word_response_time(chat_number)
    plot_person_response_time(chat_number)


# In[ ]:
for ix in range(len(sorted_chats)):
    plot(ix)
