import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/novels.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reading_lists = db.relationship('ReadingList', backref='user', lazy=True, cascade='all, delete-orphan')

class Novel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    synopsis = db.Column(db.Text, nullable=True)
    cover_image = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), nullable=False)  # Ongoing, Completed, Hiatus
    total_chapters = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tags = db.Column(db.String(500), nullable=True)  # Comma-separated tags
    reading_lists = db.relationship('ReadingList', backref='novel', lazy=True, cascade='all, delete-orphan')

class ReadingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    novel_id = db.Column(db.Integer, db.ForeignKey('novel.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Want to Read')  # Want to Read, Reading, Completed, Dropped, On Hold
    rating = db.Column(db.Integer, nullable=True)  # 1-5 stars
    review = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'novel_id'),)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    recent_novels = Novel.query.order_by(Novel.created_at.desc()).limit(6).all()
    return render_template('index.html', novels=recent_novels)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        user = User(
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/search')
def search():
    query = request.args.get('q', '')
    tag_filter = request.args.get('tag', '')
    
    novels_query = Novel.query
    
    if query:
        novels_query = novels_query.filter(
            db.or_(
                Novel.title.contains(query),
                Novel.author.contains(query)
            )
        )
    
    if tag_filter:
        novels_query = novels_query.filter(Novel.tags.contains(tag_filter))
    
    novels = novels_query.order_by(Novel.title).all()
    
    # Get all unique tags for filter dropdown
    all_tags = []
    for novel in Novel.query.all():
        if novel.tags:
            all_tags.extend([tag.strip() for tag in novel.tags.split(',')])
    unique_tags = sorted(list(set(all_tags)))
    
    return render_template('search.html', novels=novels, query=query, tag_filter=tag_filter, all_tags=unique_tags)

@app.route('/novel/<int:novel_id>')
def novel_detail(novel_id):
    novel = Novel.query.get_or_404(novel_id)
    user_status = None
    user_rating = None
    user_review = None
    
    if current_user.is_authenticated:
        reading_list = ReadingList.query.filter_by(
            user_id=current_user.id,
            novel_id=novel_id
        ).first()
        if reading_list:
            user_status = reading_list.status
            user_rating = reading_list.rating
            user_review = reading_list.review
    
    return render_template('novel.html', novel=novel, user_status=user_status, 
                         user_rating=user_rating, user_review=user_review)

@app.route('/mylist')
@login_required
def mylist():
    status_filter = request.args.get('status', '')
    
    reading_lists = ReadingList.query.filter_by(user_id=current_user.id)
    
    if status_filter:
        reading_lists = reading_lists.filter_by(status=status_filter)
    
    reading_lists = reading_lists.order_by(ReadingList.updated_at.desc()).all()
    
    # Group by status
    grouped_lists = {}
    for item in reading_lists:
        if item.status not in grouped_lists:
            grouped_lists[item.status] = []
        grouped_lists[item.status].append(item)
    
    statuses = ['Want to Read', 'Reading', 'Completed', 'Dropped', 'On Hold']
    
    return render_template('mylist.html', grouped_lists=grouped_lists, 
                         statuses=statuses, current_filter=status_filter)

@app.route('/add_to_list/<int:novel_id>', methods=['POST'])
@login_required
def add_to_list(novel_id):
    novel = Novel.query.get_or_404(novel_id)
    status = request.form.get('status')
    rating = request.form.get('rating')
    review = request.form.get('review')
    
    # Convert rating to int or None
    rating = int(rating) if rating and rating.isdigit() else None
    
    reading_list = ReadingList.query.filter_by(
        user_id=current_user.id,
        novel_id=novel_id
    ).first()
    
    if reading_list:
        reading_list.status = status
        reading_list.rating = rating
        reading_list.review = review
        reading_list.updated_at = datetime.utcnow()
    else:
        reading_list = ReadingList(
            user_id=current_user.id,
            novel_id=novel_id,
            status=status,
            rating=rating,
            review=review
        )
        db.session.add(reading_list)
    
    db.session.commit()
    flash(f'Added "{novel.title}" to your reading list!', 'success')
    return redirect(url_for('novel_detail', novel_id=novel_id))

@app.route('/remove_from_list/<int:novel_id>', methods=['POST'])
@login_required
def remove_from_list(novel_id):
    reading_list = ReadingList.query.filter_by(
        user_id=current_user.id,
        novel_id=novel_id
    ).first()
    
    if reading_list:
        db.session.delete(reading_list)
        db.session.commit()
        flash('Removed from your reading list', 'success')
    
    return redirect(url_for('mylist'))

# Initialize database with sample data
def init_sample_data():
    if Novel.query.count() == 0:
        sample_novels = [
            Novel(
                title="Solo Leveling",
                author="Chugong",
                synopsis="In a world where hunters must battle deadly monsters, the weakest hunter Sung Jinwoo gains incredible powers through a mysterious system.",
                status="Completed",
                total_chapters=200,
                tags="Action, Adventure, Fantasy, System"
            ),
            Novel(
                title="The Beginning After The End",
                author="TurtleMe",
                synopsis="King Grey has unrivaled strength, wealth, and prestige in a world governed by martial ability. However, solitude lingers closely behind those with great power.",
                status="Ongoing",
                total_chapters=175,
                tags="Fantasy, Reincarnation, Adventure, Romance"
            ),
            Novel(
                title="Omniscient Reader's Viewpoint",
                author="Sing-Shong",
                synopsis="Only I know the end of this world. One day, our world finds itself merged with the novel I was reading.",
                status="Completed",
                total_chapters=551,
                tags="Action, Fantasy, System, Apocalypse"
            ),
            Novel(
                title="Trash of the Count's Family",
                author="Yoo Ryeo Han",
                synopsis="When I opened my eyes, I was inside a novel. I became a part of that novel as the trash of a Count.",
                status="Ongoing",
                total_chapters=800,
                tags="Fantasy, Adventure, System, Reincarnation"
            ),
            Novel(
                title="Martial Peak",
                author="Momo",
                synopsis="The journey to the martial peak is a lonely, solitary and long one. In the face of adversity, you must survive and remain unyielding.",
                status="Completed",
                total_chapters=6000,
                tags="Martial Arts, Adventure, Harem, Fantasy"
            )
        ]
        
        for novel in sample_novels:
            db.session.add(novel)
        
        db.session.commit()
        print("Sample data initialized!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_sample_data()
    app.run(debug=True)