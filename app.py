from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Book.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Avoids warning messages
db = SQLAlchemy(app)

# Books db model class
class Book(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(600), nullable=False)
    status = db.Column(db.String(400), nullable=False)
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"{self.sno} - {self.title}"

@app.route("/", methods = ['GET', 'POST'])
def home_view():
    if request.method == 'POST':
        #print(request.form['title'])
        #print("POST method called")
        backend_book_title = request.form['title']
        backend_book_description = request.form['description']
        backend_book_status = request.form['status']
        
        new_book = Book(title=backend_book_title, description = backend_book_description, status = backend_book_status)
        db.session.add(new_book) # Add the new book to the session in db
        db.session.commit() # Commit the changes to save in DB

    print("Book added successfully!") # printing to console
    book_list = Book.query.all() # fetch all books from db
    return render_template('index.html', books = book_list) # passing 'book_list' as data variable using Jinja2 template to index.html file as 'books' variable

# route to get list Books
@app.route("/books")
def books():
    # book_list = Book.query.all()
    # print(book_list)
    return "<p>This is Book List page!!</p>"

# route to delete book by its sno
@app.route("/delete/<int:bookSno>")
def delete(bookSno):
    # book = db.session.execute(db.select(Book).filter_by(sno = bookSno)).scalar_one()
    book = Book.query.filter_by(sno = bookSno).first()
    db.session.delete(book)
    db.session.commit()
    #return redirect("/")
    return redirect(url_for('home_view')) #reverse url mapping from view to route url

# route for update book info
@app.route("/update/<int:bookSno>", methods = ['GET', 'POST'])
def update(bookSno):
    # 2] once fields updated - update the book info in db
    if request.method == 'POST':
        # newly updated fields info
        new_title = request.form['title']
        new_description = request.form['description']
        new_status = request.form['status']
        # same old book fetched - and field values updated with new once
        updatedBook = Book.query.filter_by(sno = bookSno).first()
        updatedBook.title = new_title
        updatedBook.description = new_description
        updatedBook.status = new_status
        updatedBook.date_created = datetime.now(timezone.utc)
        db.session.add(updatedBook) # Add the new book to the session in db
        db.session.commit() # Commit the changes to save in DB
        return redirect("/")

    # 1] this old book is fetched first - fields auto populate info - displays update.html page
    oldBook = Book.query.filter_by(sno = bookSno).first()
    return render_template('update.html', book_found = oldBook) 

# route to search Book by Title
@app.route("/search", methods = ["GET"])
def search():
    search_title = request.args.get('searchTitle')  # gets the value from ?searchTitle=...
    print(search_title)
   # search_results = Book.query.filter_by(title = f"%{search_title}%").all()
    # Run a case-insensitive search
    search_results = Book.query.filter(Book.title.ilike(f"%{search_title}%")).all()
    print(search_results)
    return render_template("index.html", books=search_results)

# route to about info
@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run(debug=True, port=8000)