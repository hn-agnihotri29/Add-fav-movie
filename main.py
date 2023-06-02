from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
MOVIE_DETAIL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_API_KEY = "92f54424a3465deeb0b6b58fedfec19b"
IMG_PATH = "https://www.themoviedb.org/t/p/original"



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
bootstrap = Bootstrap(app)

db = SQLAlchemy()
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies.db"
db.init_app(app)

app.app_context().push()


class EditForm(FlaskForm):
    change_rating = StringField(label="Your Rating Out of 10 e.g. 7.5", validators=[DataRequired()])
    change_review = StringField(label="Your Review", validators=[DataRequired()])
    submit_button = SubmitField(label="Down")


class MovieTitle(FlaskForm):
    movie_title = StringField(label="Movie Title", validators=[DataRequired()])
    submit = SubmitField("Add Movie")


# CREATE TABLE
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer)
    review = db.Column(db.String(250),nullable=True)
    img_url = db.Column(db.String(250), nullable=True)


# db.create_all()


@app.route("/")
def home():
    all_movies = Movie.query.all()
    # This line loops through all the movies
    for i in range(len(all_movies)):
        # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route("/update", methods=['GET', 'POST'])
def update():
    form = EditForm()
    movie_id = request.args.get('id')
    movie_selected = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie_selected.rating = float(form.change_rating.data)
        movie_selected.review = form.change_review.data
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("edit.html", movie=movie_selected, form=form)


@app.route('/delete')
def delete():
    movie_id = request.args.get('id')
    movie = db.get_or_404(Movie, movie_id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=['GET', 'POST'])
def add():
    form = MovieTitle()
    if form.validate_on_submit():
        param = {
            "api_key": MOVIE_DB_API_KEY,
            "query": form.movie_title.data
        }
        response = requests.get(MOVIE_DB_SEARCH_URL, params=param)
        data = response.json()['results']
        return render_template("select.html", options=data)

    return render_template("add.html", form=form)


@app.route("/select")
def select_movie():
    movie_id = request.args.get('id')
    response = requests.get(f"{MOVIE_DETAIL}/{movie_id}", params={"api_key": MOVIE_DB_API_KEY})
    data = response.json()

    new_movie = Movie(
        title=data["title"],
        year=data["release_date"].split("-")[0],
        description=data['overview'],
        img_url=f"{IMG_PATH}{data['poster_path']}"
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('update', id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
