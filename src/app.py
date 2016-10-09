import os
import random
import json
import uuid
import operator
from datetime import datetime
import time
from flask import (Flask, render_template, request, 
                    send_from_directory, redirect, url_for)

__author__ = "jcamer32"

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'tiff']) #server side file type validation
app.config['MAX_CONTENT_LENGTH'] = 0.5 * 1024 * 1024 #total maximum upload set to 500KB (multiple uploads)
    #note unfortunately I could not figure out how to ensure individual file size max

# sort through metadata files and return the top 5 usernames
def user():
    users = {}
    for file in os.listdir(path="./metadata"):
        if file != '.DS_Store':
            json_url = open("metadata/"+file)
            json_data = json.load(json_url)
            if json_data["username"] not in users:
                users[json_data["username"]] = 1
            else:
                users[json_data["username"]] += 1
    sorted_users = sorted(users.items(), key=operator.itemgetter(1))
    sorted_users.reverse()
    top_5_users = [str(sorted_users[0][0])+' ('+(str(sorted_users[0][1])+')'),
            str(sorted_users[1][0])+' ('+(str(sorted_users[1][1])+')'),
            str(sorted_users[2][0])+' ('+(str(sorted_users[2][1])+')'),
            str(sorted_users[3][0])+' ('+(str(sorted_users[3][1])+')'),
            str(sorted_users[4][0])+' ('+(str(sorted_users[4][1])+')')]
    return top_5_users

# sort through metadata files and return the top 5 tag
def top_tags():
    tags = {}
    for file in os.listdir(path="./metadata"):
        if file != '.DS_Store':
            json_url = open("metadata/"+file)
            json_data = json.load(json_url)
            try:
                if json_data["tag"] not in tags:
                    tags[json_data["tag"]] = 1
                else:
                    tags[json_data["tag"]] += 1
            except KeyError:
                pass
    sorted_tags = sorted(tags.items(), key=operator.itemgetter(1))
    sorted_tags.reverse()
    top_5_tags = [str(sorted_tags[0][0])+' ('+(str(sorted_tags[0][1])+')'),
            str(sorted_tags[1][0])+' ('+(str(sorted_tags[1][1])+')'),
            str(sorted_tags[2][0])+' ('+(str(sorted_tags[2][1])+')'),
            str(sorted_tags[3][0])+' ('+(str(sorted_tags[3][1])+')'),
            str(sorted_tags[4][0])+' ('+(str(sorted_tags[4][1])+')')]
    return top_5_tags

# server side file validation. used in upload route
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# return list of tuples of each image name and corresponding unique id
def get_files():
    username = 'all users'
    image_names = os.listdir('./images')
    image_names.remove('.DS_Store')
    image_ids = []
    for image_name in image_names:
        for file in os.listdir(path="./metadata"):
            if file != '.DS_Store':
                json_url = open("metadata/"+file)
                json_data = json.load(json_url)
                if json_data["filename"] == image_name:
                    image_ids.append(json_data["id"])
    image_names = list(zip(image_names, image_ids))
    return image_names

# upload new comments on large image overlay
@app.route('/comments', methods=['POST'])
def receive_comments():
    file_id=request.form['file_id']
    comment_dict = {}
    comment_dict["comment_user"] = request.form['username']
    comment_dict["comment"]= request.form['write_comment']

    timestamp = datetime.now()
    timestamp = time.mktime(timestamp.timetuple())
    old_json =  open('./metadata/'+file_id+'.json', 'r')
    old_data =  json.load(old_json)
    try:
        old_data["comments"]
    except KeyError:
        old_data["comments"] = []
    updated_data = old_data["comments"].append(comment_dict)
    with open('./metadata/'+file_id+'.json', 'w') as outfile:
        json.dump(old_data, outfile)
        # outfile.write('\n')
    return redirect(url_for('get_gallery'))

# landing redirect to main gallery page
@app.route('/')
def landing():
    return redirect(url_for('get_gallery'))

# render upload.html
@app.route("/upload")
def index():
    return render_template("upload.html")

# display gallery of images uploaded in last 48 hours
@app.route("/recent")
def recently_uploaded():
    image_names = os.listdir('./images')
    image_names.remove('.DS_Store')
    image_ids = []
    recent_image_names = []
    timenow = datetime.now()
    timenow = time.mktime(timenow.timetuple())
    for file in os.listdir(path="./metadata"):
        if file != '.DS_Store':
            json_url = open("metadata/"+file)
            json_data = json.load(json_url)
            if timenow - json_data["timestamp"] < 172800: #file uploaded less than 48 hours ago
                image_ids.append(json_data["filename"])
                image_ids.append(json_data["id"])
    print(image_ids)
    for image_name in image_names:
        if image_name in image_ids:
            recent_image_names.append(image_name)

    recent_image_names = list(zip(recent_image_names, image_ids))
    print(recent_image_names)
    return render_template("recent_gallery.html", image_names=recent_image_names)


# accepts form data from upload.html inclunding files, username and tag and timestamps the upload
@app.route("/upload", methods=['POST'])
def upload():
    username = request.form['username'].lower()
    timestamp = datetime.now()
    timestamp = time.mktime(timestamp.timetuple())
    if username == "":
        username = "anon"+str(random.randint(1000,9999))
            # need unique - uuid?
    target = os.path.join(APP_ROOT, 'images')
    if not os.path.isdir(target):
        os.mkdir(target)
    ids = {}
    tag = request.form['tag'].lower()
    for file in request.files.getlist("file"):

        if allowed_file(file.filename):
            
            filename = file.filename
            ids["id"] = str(uuid.uuid1())
            ids["filename"] = username+'.'+filename
            ids["username"] = username
            ids["timestamp"] = timestamp
            if tag != '':
                ids["tag"] = '#'+tag
            destination = "/".join([target, username+'.'+filename])
            file.save(destination)
            with open('./metadata/'+ids["id"]+'.json', 'a') as outfile:
                json.dump(ids, outfile)
                outfile.write('\n')
    return redirect(url_for('get_gallery'))

# make path available for invidual image files
@app.route('/gallery/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)

# renders gallery of uploads from each user
@app.route('/<username>')
def get_username_gallery(username):
    image_names = get_files()
    user_image_names = []
    count = 1
    for image_name in image_names:
        if image_name[0].startswith(username):
            user_image_names.append(image_name)

        count+=1
    print(user_image_names)
    return render_template("user_gallery.html", image_names=user_image_names, username=username)

# makes json files available for js to request and read
@app.route('/metadata/<json_file>', methods=["GET","POST"])
def serve_json(json_file):
    return send_from_directory("metadata", json_file)

# renders gallery of uploads of each defined tag
@app.route('/tag/<tagname>')
def get_tag_gallery(tagname):
    chosen_tag = []
    for file in os.listdir(path="./metadata"):
        if file != '.DS_Store':
            json_url = open("metadata/"+file)
            json_data = json.load(json_url)
            try:
                if json_data["tag"][1:] == tagname:
                    chosen_tag.append([json_data["filename"],json_data["id"]])
            except KeyError:
                pass
    return render_template("tag_gallery.html", image_names=chosen_tag, tagname=tagname)
    # return render_template("gallery.html", image_names=chosen_tag)

#main gallery route. includes all images and links to 5 most active users and 5 most popular tags 
@app.route('/all')
def get_gallery():
    username= "all"
    image_names = get_files()
    top_user_1 = "top_user_1"
    top_user_2 = "top_user_2"
    top_user_3 = "top_user_3"
    top_user_4 = "top_user_4"
    top_user_5 = "top_user_5"
    top_tag_1 = "top_tag_1"
    top_tag_2 = "top_tag_2"
    top_tag_3 = "top_tag_3"
    top_tag_4 = "top_tag_4"
    top_tag_5 = "top_tag_5"

    try:
        top_user_1 = user()[0]
        top_user_2 = user()[1]
        top_user_3 = user()[2]
        top_user_4 = user()[3]
        top_user_5 = user()[4]
        top_tag_1 = top_tags()[0]
        top_tag_2 = top_tags()[1]
        top_tag_3 = top_tags()[2]
        top_tag_4 = top_tags()[3]
        top_tag_5 = top_tags()[4]
    except IndexError:
        pass
    return render_template("gallery.html", image_names=image_names, 
        username=username, top_user_1=top_user_1, top_user_2=top_user_2, top_user_3=top_user_3,
        top_user_4=top_user_4, top_user_5=top_user_5, top_tag_1 = 'tag/'+str(top_tag_1), 
        top_tag_2 = 'tag/'+str(top_tag_2),top_tag_3 = 'tag/'+str(top_tag_3), top_tag_4 = 'tag/'+str(top_tag_4),
        top_tag_5 = 'tag/'+str(top_tag_5))

@app.route('/about')
def about():
    return render_template('about.html')

app.run(port=8000, debug=True, host='127.0.0.1')