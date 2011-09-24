import random
import time
import logging
#import facebook

WINDOW_SIZE = 8
LATEST_DATE = '2015-12-31T23:59:00+0000'



##################################
# Conversion to FB objects
##################################
def _to_fb_status(user, graph, message, t): #, likes, comments, commenters):
    friends = graph.get_connections("me", "friends")
    ret = {}
    ret["id"] = "0" # do something interesting here?
    ret["from"] = {"name": user.name,
                   "id": user.id}
    ret["message"] = message
    ret["created_time"] = t
    
    return ret

    #likers = []
    #for name in likes:
    #    likers.append(get_friend(name,friends["data"]))
    #ret["likes"] = {"data": likers}
    
    #c = []
    #for i in range(len(comments)):
    #    new_c = {}
    #    new_c["id"] = "0_0" # do something interesting here?
    #    new_c["from"] = get_friend(commenters[i],friends["data"])
    #    new_c["message"] = message
    #    new_c["created_time"] = t
    #    new_c["can_remove"] = True
    #    c.append(new_c)
    #ret["comments"] = {"data": c,
    #                   "count": len(c)}

def _to_fb_post(user, graph, new_post, new_writer, new_date):
    friends = graph.get_connections("me", "friends")
    ret = {}
    #ret["id"] = "0" # do something interesting here?
    ret["from"] = get_friend(new_writer, friends["data"])
    ret["to"] = {"data": [{"name":user.name,
                           "id": user.id}
                          ]}
    ret["message"] = new_post
    ret["type"] = "status"

    ret["created_time"] = new_date
    #ret["updated_time"] = new_date

    # maybe add some comment stuff
    #ret["comments"] = {"count": 0}
    
    return ret

def _to_fb_picture(user,graph, new_poster, url, comments, commenters, t):
    friends = graph.get_connections("me", "friends")
    ret = {}
    ret["id"] = "0"
    ret["from"] = get_friend(new_poster,friends["data"])
    ret["source"] = url
    ret["created_time"] = t
    ret["updated_time"] = t
    
    new_comments = []
    for i in range(len(comments)):
        new_d = {}
        new_d["id"] = "0_0"
        new_d["from"] = get_friend(commenters[i],friends["data"])
        new_d["message"] = comments[i]
        new_d["created_time"] = t
        new_comments.append(new_d)
    ret["comments"] = {"data": new_comments}
    
    return ret

# END conversion functions
        

#######################################################
# Analyze and generate new content
#######################################################

# Returns count pictures that the user is tagged in, plus his or her profile picture
def get_tagged_pictures(user, count):
    pictures = user["photos"]["data"]

    picture_urls = []
    for picture in pictures:
        tags = picture["tags"]["data"]

        # see if the user is tagged in this picture
        for tag in tags:
            if tag["name"] == user["name"]:
                picture_urls.append(picture["source"]) # "picture" instead?
        
        if len(picture_urls) > count:
            break

    picture_urls.append(user["picture"]) # this might not actually work
    return picture_urls


def generate_new_photos(user, count):
    urls = []
    pictures = get_tagged_pictures(user, count)
    for picture in pictures:
        # call open CV stuff to get new picture
        urls.append(url_to_new_picture) # can we get a url for this?
        pass

    (posters, num_comments, comments, commenters) = analyze_tagged_photos(user)
    comments_str = ' '.join(comments)

    new_posters = choose_subset(posters, count)

    updates = []
    for i in range(count):
        num_commenters = random.randint(0,num_comments * 2)
        new_commenters = choose_subset(commenters, num_commenters)
        
        new_comments = []
        for i in range(num_commenters):
            new_comments.append(generate_text(comments_str, WINDOW_SIZE))
            
        new_time = random_date()
                             
        updates.append(_to_fb_picture(user, graph, new_posters[i], url[i], new_comments, new_commenters, new_time))
        
    
    pass


def analyze_tagged_photos(user):
    pictures = user["photos"]["data"]
    posters = {}
    commenters = {}
    comments = []
    num_comments = 0

    for picture in pictures:
        poster = picture["from"]["name"]
        if posters.get(poster):
            posters[poster] += 1
        else:
            posters[poster] = 1
        
        comments = picture["comments"]["data"]
        for comment in comments:
            numcomments += 1
            commenter = comment["from"]["name"]
            comments.append(comments["message"])
            if commenters.get(commenter):
                commenters[commenter] += 1
            else:
                commenters[commenter] = 1
    
    return (posters, num_comments, comments, commenters)
    
    

def generate_new_friend(user):
    pass

# generates a name for a fictitious new friend
def generate_friend_name(user):
    friends = user["friends"]["data"]
    friend_names = []
    for friend in friends:
        friend_names.append(friend["name"])

    first = random.randint(0,len(friend_names))
    last = random.randint(0,len(friend_names))
    
    split_name = friend_list[first].split(' ')
    first_name = split_name[0]
    split_name = friend_list[last].split(' ')
    last_name = split_name[len(split_name)-1]

    return first_name + ' ' + last_name

# takes an object representing a facebook user and returns information about 
# that user's status updates and comments
def analyze_status_updates(user, graph):
    statuses = graph.get_connections("me", "statuses")
    messages = []
    #num_comments = 0
    #num_likes = 0
    #likers = {}
    for status in statuses["data"]:
        messages.append(status["message"])
    return messages
        #comments = graph.get_connections(status["id"], "comments")
        #num_comments += len(comments["data"])

        #likes = graph.get_connections(status["id"], "likes")
        #num_likes += len(likes["data"])
        #for liker in likes["data"]:
        #    if likers.get(liker["name"]):
        #        likers[liker["name"]] += 1
        #    else:
        #        likers[liker["name"]] = 1
        
        
            
    #likes_per_status = num_likes / len(statuses)
    #comments_per_status = num_comments / len(statuses)
    
    #return (messages,
    #        likers,
    #        likes_per_status,
    #        comments_per_status)

# takes an object representing a facebook user and returns information about 
# messages that other people have posted on his wall 
def analyze_incoming_wall_posts(user, graph):
    # get data from users commenting on your statuses
    #statuses = graph.get_connections("me", "statuses")
    #writers = {}
    #messages = []
    #for status in statuses["data"]:
    #    comments = graph.get_connections(status["id"], "comments")
    #    for comment in comments["data"]:
    #        writer = comment["from"]["name"]
    #        if writers.get(writer):
    #            writers[writer] += 1
    #        else:
    #            writers[writer] = 1
    #        messages.append(comment["message"])

    # get data from users posting on your wall
    messages = []
    writers = {}
    posts = graph.get_connections("me", "feed")
    for post in posts["data"]:
        writer = post["from"]["name"]
        if writers.get(writer):
            writers[writer] += 1
        else:
            writers[writer] = 1
        if "message" in post:
            messages.append(post["message"])
        
    logging.debug(str(writers))
    return (messages, writers)

# given a name, returns the facebook dictionary corresponding
# to that friend
def get_friend(friend_name, friendlist):
    for friend in friendlist:
        if friend["name"] == friend_name:
            return {"name": friend["name"],
                    "id": friend["id"]}

    # default
    return {"name": "Unknown",
            "id" : "0"}


def generate_status_updates(user, graph, count):
    #friends = graph.get_connections("me", "friends")
    #(user_messages, likers, avg_likes, avg_comments) = analyze_status_updates(user, graph)
    user_messages = analyze_status_updates(user, graph)
    user_messages_str = ' '.join(user_messages)
#(friend_messages, writers) = analyze_incoming_wall_posts(user, graph)
    #friend_messages_str = ' '.join(friend_messages)
    updates = []
    for i in range(count):
        # generate new status
        new_status = generate_text(user_messages_str, WINDOW_SIZE)
        
        # generate likers for this new status
        #num_likes = random.randint(0, avg_likes * 2)
        #new_likers = choose_subset(likers, num_likes) # put in object

        # generate comments for this new status
        #num_comments = random.randint(0, avg_comments * 2)
        #new_commenters = choose_subset(writers, num_comments)
        #new_comments = []
        #for c in new_commenters:
        #    new_comments.append(generate_text(friend_messages_str, WINDOW_SIZE))

        # generate time for this new status
        new_date = random_date()

        # wrap it all into a facebook-like object
        updates.append(_to_fb_status(user, graph, new_status, new_date))
                                     #new_likers, 
                                     #new_comments, 
                                     #new_commenters))
                       
    return updates

def generate_wall_posts(user, graph, count):
    friends = graph.get_connections("me", "friends")
    #user_messages = analyze_status_updates(user)
    #user_messages_str = ' '.join(user_messages)
    (friend_messages, writers) = analyze_incoming_wall_posts(user, graph)
    friend_messages_str = ' '.join(friend_messages)
    
    updates = []
    for i in range(count):
        # generate new wall post
        new_post = generate_text(friend_messages_str, WINDOW_SIZE)

        # generate time for this new post
        new_date = random_date()
        
        # generate writer for this post
        new_writer = choose_subset(writers, 1)[0]
        
        updates.append(_to_fb_post(user, graph, new_post, new_writer, new_date))

    return updates


def choose_subset(d, size):
    if size == 0:
        return []
    pop = []
    for key in d:
        pop.append(key * d[key])
    if size > len(pop):
        size = len(pop)
    return random.sample(pop, size)

### END Analyze and Generate

#######################################
# Text generation
######################################
def choose_next(d):
    values = []
    for key in d:
        values += key * d[key]
    if len(values) == 0:
        return ' '
    else:
        return random.choice(values)

def find_occurences(seed, src):
    i = 0
    d = {}
    while i < len(src) - 1:
        idx = src.find(seed, i , len(src) - 1)
        if idx == -1:
            break
        next = src[idx+len(seed)]
        if d.get(next):
            d[next] += 1
        else:
            d[next] = 1
        i = idx + len(seed)

    return d

def get_seed(src, window):
    if len(src) == 0:
        return ' '
    r = random.randint(0, len(src) - 1)
    while src[r-1] != ' ' or r + window > len(src):
        r = random.randint(0, len(src) - 1)
    seed = src[r:r+window]
    return seed

def generate_text(src, window):
    line = ''

    seed = get_seed(src, window)
    line += seed

    while len(line) < 150:
        d = find_occurences(seed, src)
        n = choose_next(d)
        line += n
        seed = seed[1:] + n

    return line
##### END text generation

##################################
# Date generation
##################################
def propagate_time_diff(start, end, format, prop):
    stime = time.mktime(time.strptime(start, format))
    etime = time.mktime(time.strptime(end, format))

    ptime = stime + prop * (etime - stime)

    return time.strftime(format, time.localtime(ptime))


def random_date():
    start = time.strftime('%Y-%m-%dT%H:%M:%S+0000', time.localtime())
    return propagate_time_diff(start, LATEST_DATE, '%Y-%m-%dT%H:%M:%S+0000', random.random())
#### end date generation functions

if __name__ == '__main__':
    fname = 'dostoyevsky.txt'
    infile = open(fname,'rU')
    data = infile.read()
    data = data.replace('\n', ' ')
    
    status = generate_text(data, 10)
    print status
