from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class TeamMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    tasks = db.relationship('Task', backref='team_member', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    team_member_id = db.Column(db.Integer, db.ForeignKey('team_member.id'), nullable=False)

@app.route('/')
def index():
    team_members = TeamMember.query.all()
    # Calculate the number of pending tasks for each team member
    pending_tasks_count = {}
    for member in team_members:
        pending_tasks_count[member.id] = len([task for task in member.tasks if not task.completed])
    
    return render_template('index.html', team_members=team_members, pending_tasks_count=pending_tasks_count)

@app.route('/add_member', methods=['POST'])
def add_member():
    name = request.form.get('name')
    new_member = TeamMember(name=name)
    db.session.add(new_member)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/add_task/<int:member_id>', methods=['POST'])
def add_task(member_id):
    description = request.form.get('description')
    new_task = Task(description=description, team_member_id=member_id)
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if request.method == 'POST':
        task.description = request.form.get('description')
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_task.html', task=task)

@app.route('/remove_task/<int:task_id>')
def remove_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/mark_completed/<int:task_id>')
def mark_completed(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = True
    task.completed_at = datetime.utcnow()
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Wrap database creation inside the app context
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)
