from flask import Flask, redirect, render_template, url_for, request, session, abort, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
import imghdr
import os
from random import *

app = Flask(__name__)

    # CONFIGS
app.config['SQLAlchemy_DATABASE_URI'] = "sqlite:///Mini-Git.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_BINDS'] = False

app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024

app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif', '.html', '.css', '.js', '.ico']

app.config['UPLOAD_PATH'] = 'static/uploads'

app.config['SECRET_KEY'] = os.urandom(32)

    # variables
id_developer = -1

    # Classes
DB = SQLAlchemy(app)

class Developers(DB.Model):
    id_developer = DB.Column(DB.Integer, primary_key=True)
    name = DB.Column(DB.String(100), nullable=False)
    password = DB.Column(DB.String(100), nullable=False)

    def __repr__(self):
        return '<Developer %r>' % self.id_developer

class Projects(DB.Model):
    id = DB.Column(DB.Integer, primary_key=True)
    title = DB.Column(DB.String(100), nullable=False)
    intro = DB.Column(DB.String(300), nullable=False)

    date = DB.Column(DB.DateTime, default=datetime.utcnow)

    url = DB.Column(DB.Text, nullable=False)
    name_visiable = DB.Column(DB.Text, nullable=False)
    name_invisiable = DB.Column(DB.Text, nullable=False)

    main_file = DB.Column(DB.Text)

    file_1st = DB.Column(DB.Text)
    file_2nd = DB.Column(DB.Text)
    file_3rd = DB.Column(DB.Text)

    def __repr__(self):
        return '<Article %r>' % self.id


DB.create_all()

    # Logging
@app.route("/log_in/<int:log_warning>", methods=["POST", "GET"])
def logIn(log_warning):
    if request.method == "POST":
        developer_account = False

        name = request.form["name"]
        password = request.form["password"]

        developers_accounts = Developers.query.order_by().all()
        
        # по всей бд ищем пользователя с такими данными
        for developer in developers_accounts:
            print(f"{developer.name} - {name}")
            print(f"{developer.password} - {password}")
            if developer.name.lower() == name.lower() and developer.password.lower() == password.lower():
                developer_account = developer
                print("Developer Was Found", developer_account.id_developer)

        if not developer_account:
            developer = Developers(name=name, password=password)

            try:
                DB.session.add(developer) 
                DB.session.commit()
                print("CREATE Developer:", developer.id_developer)
            except:
                print("WARNING Account")
        
        try:

            print("Developer_ID",developer.id_developer)
            if log_warning == 1:
                return redirect(f'/1/{developer.id_developer}/create')

            return redirect(f'/{developer.id_developer}')

        except Exception as _Ex:
            return str(_Ex)

    else:
        return render_template("log_in.html")

    # Index
@app.route("/")
def index_none():
    print("id_developer in none", id_developer)
    
    try:
        if id_developer == -1:
            return redirect('/log_in/0')
        return render_template("index.html", id_developer=id_developer)
        
    except Exception as _Ex:
        print("Exeption in Index without Id\n", _Ex)
        return redirect('/log_in/0')

    

@app.route("/<int:id_developer>", methods=["POST", "GET"])
def index(id_developer):
    print("id_developer", id_developer)
    try:       
        projects = Projects.query.order_by(Projects.date.desc()).all()

    except Exception as _Ex:
        print("Exeption in Index with Id\n", _Ex)
        return redirect('/log_in/0')

    if request.method == "POST":
        clear_list = list()

        request_search = request.form["search"]
        print("SEARCH", request_search)
        
        for project in projects:
            if request_search in project.title or request_search in project.intro:
                clear_list.append(project)

        projects = clear_list
    
    return render_template("index.html", id_developer=id_developer, projects=projects)


    # Create repository
@app.route("/<int:warning_log>/<int:id_developer>/create", methods=["POST", "GET"])
def create_repository(id_developer, warning_log):
    global list_form

    name = ''
    title = ''
    url = ''
    intro = ''
    

    print("id_developer", id_developer)
    if request.method == "POST":
        name = request.form['name']
        title = request.form['title']
        url = request.form['url']
        intro = request.form['intro']
        

        list_form = (name, title, url, intro)
        print(list_form)

        returning = True

        for i in range(len(list_form)):
            if list_form[i] == '':
                returning = False

            # Creating
        print("Returning:", returning)

        if returning:

            try:

                developer = Developers.query.get(id_developer)
                print("Developer_Name", developer.name)
                developer = developer.name

            except:
                return redirect('/log_in/1')

            try:
                project = Projects(title=title, intro=intro, 
                        name_invisiable=developer, 
                        name_visiable=name, url=url,
                        file_1st='', file_2nd='', file_3rd='',
                        main_file='') 

                DB.session.add(project)
                DB.session.commit()
                print("Project Id",project.id)
                # return redirect(f'/download/{notice.id}/{id_shoper}')
                return redirect(f'/download/{project.id}/{id_developer}')

            except Exception as _Ex:
                return str(_Ex)

    elif warning_log == 1:
        # (name, title, url, intro)
        try:
            print(list_form)
            name = list_form[0]
            title = list_form[1]
            url = list_form[2]
            intro = list_form[3]
        except Exception as _Ex:

            print("WArning in log_1\n", _Ex)
            list_form = ('', '', '', '')

        return render_template("create.html", warning_log=warning_log, id_developer=id_developer, name=name, title=title, url=url, intro=intro)


    try:
        return render_template("create.html", id_developer=id_developer)
    
    except Exception as _Ex:
        print("Exeption in Create\n", _Ex)
        return redirect('/log_in/0')

    # Profile
@app.route("/<int:id_developer>/profile")
def profile(id_developer):
    print("id_developer", id_developer)

    projects = Projects.query.order_by(Projects.date.desc()).all()
    developer_list = list()

    try:
        developer = Developers.query.get(id_developer)
        developer_name = developer.name
    except:
        return redirect('/log_in/0')

    print("SHOPER_NAME", developer.name)

    for project in projects:
        if project.name_invisiable == developer_name:
            developer_list.append(project)

    print("LENGTH", len(developer_list))

    try:
        return render_template("profile.html", projects=developer_list, id_developer=id_developer, developer_name=developer_name)
    
    except Exception as _Ex:
        print("Exeption in Profile\n", _Ex)
        return redirect('/log_in/0')

    # Detail Post
@app.route("/posts/<int:id_project>/<int:id_developer>/detail")
def post_detail(id_developer, id_project):
    print("id_developer", id_developer)
    
    try:
        project = Projects.query.get(id_project)

        return render_template("project_detail.html", project=project, id_developer=id_developer)

    except Exception as _Ex:
        print("Exeption in Post Detail\n", _Ex)
        return redirect('/log_in/0')

    # Downloading Files

def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        print("FORMAT is", format)
        return None
    return '.' + (format if format != 'jpeg' else 'jpg')

@app.errorhandler(413)
def too_large(e):
    return "File is too large", 413

@app.route('/download/<int:project_id>/<int:id_developer>') 
def downloading(project_id, id_developer):
    global counter_files
    files = os.listdir(app.config['UPLOAD_PATH'])
    print("FILES", files)
    print(1)
    counter_files = 0
    return render_template('download.html', files=files, project_id=project_id, id_developer=id_developer)

@app.route('/download/<int:project_id>/<int:id_developer>', methods=['POST'])
def upload_files(project_id, id_developer):
    global counter_files
    print(2)
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        # проверка на расширение
        file_ext = os.path.splitext(filename)[1]
        print("FILE_EXT", file_ext)
        # or \ # file_ext != validate_image(uploaded_file.stream)

        if not (file_ext in app.config['UPLOAD_EXTENSIONS']) :
            return "Invalid file", 400
            # download
        
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
       
        # Добавление к посту
        print("FILENAME",filename)
        try:

            project = Projects.query.get(project_id)

            if file_ext == '.html':
                project.main_file = filename
                
            else:
                if counter_files == 0:
                    project.file_1st = filename
                elif counter_files == 1:
                    project.file_2nd = filename
                elif counter_files == 2:
                    project.file_3rd = filename 

            DB.session.commit()

        except Exception as _Ex:
            print("WARNING IN DOWNLOADING")
            print(_Ex)

        print("Project", project_id)
    
    return 'H1!', 204

@app.route('/download/<int:project_id>/<int:id_developer>/uploads/<string:filename>')
def upload(filename, project_id, id_developer):
    print(3)
    print("FILENAME2",filename)
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

    # Delete project
@app.route("/<int:id_project>/<int:id_developer>/delete", methods=["POST", "GET"])
def delete_repository(id_developer, id_project):
    try:
        project = Projects.query.get_or_404(id_project)
    except:
        return redirect('/log_in/10')

    try:
        DB.session.delete(project)
        DB.session.commit()
        print("ID_DELETED", id)
        return redirect(f'/{id_developer}')

    except Exception as _Ex:
        print("Mistake in delete project\n", _Ex)

if __name__ == "__main__":
    app.run(debug=True)
