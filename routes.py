from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import app, db
from models import DSAQuestion, User
from sqlalchemy import or_
from auth import auth_bp

# Register authentication blueprint
app.register_blueprint(auth_bp)

@app.route('/')
@login_required
def index():
    """Main page showing all DSA questions with search and filter functionality"""
    
    # Get search and filter parameters
    search_query = request.args.get('search', '')
    difficulty_filter = request.args.get('difficulty', '')
    topic_filter = request.args.get('topic', '')
    
    # Start with base query - only show current user's questions
    query = DSAQuestion.query.filter_by(user_id=current_user.id)
    
    # Apply search filter
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                DSAQuestion.question_name.ilike(search_pattern),
                DSAQuestion.topic_name.ilike(search_pattern)
            )
        )
    
    # Apply difficulty filter
    if difficulty_filter:
        query = query.filter(DSAQuestion.difficulty_level == difficulty_filter)
    
    # Apply topic filter
    if topic_filter:
        query = query.filter(DSAQuestion.topic_name.ilike(f"%{topic_filter}%"))
    
    # Get all questions
    questions = query.order_by(DSAQuestion.created_at.desc()).all()
    
    # Get unique topics and difficulties for filter dropdowns - only from current user's questions
    all_topics = db.session.query(DSAQuestion.topic_name).filter_by(user_id=current_user.id).distinct().all()
    topics = [topic[0] for topic in all_topics]
    
    difficulties = ['Easy', 'Medium', 'Hard']
    
    return render_template('index.html', 
                         questions=questions, 
                         topics=topics, 
                         difficulties=difficulties,
                         current_search=search_query,
                         current_difficulty=difficulty_filter,
                         current_topic=topic_filter)

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_question():
    """Add a new DSA question"""
    
    if request.method == 'POST':
        try:
            # Get form data
            topic_name = request.form.get('topic_name', '').strip()
            question_name = request.form.get('question_name', '').strip()
            difficulty_level = request.form.get('difficulty_level')
            question_link = request.form.get('question_link', '').strip()
            
            # Approach 1 (required)
            approach1_description = request.form.get('approach1_description', '').strip()
            approach1_time_complexity = request.form.get('approach1_time_complexity', '').strip()
            
            # Approach 2 (optional)
            approach2_description = request.form.get('approach2_description', '').strip()
            approach2_time_complexity = request.form.get('approach2_time_complexity', '').strip()
            
            # Approach 3 (optional)
            approach3_description = request.form.get('approach3_description', '').strip()
            approach3_time_complexity = request.form.get('approach3_time_complexity', '').strip()
            
            # Validation
            if not topic_name:
                flash('Topic name is required!', 'error')
                return render_template('add_question.html')
            
            if not question_name:
                flash('Question name is required!', 'error')
                return render_template('add_question.html')
            
            if not difficulty_level:
                flash('Difficulty level is required!', 'error')
                return render_template('add_question.html')
            
            if not approach1_description:
                flash('At least one approach description is required!', 'error')
                return render_template('add_question.html')
            
            if not approach1_time_complexity:
                flash('Time complexity for approach 1 is required!', 'error')
                return render_template('add_question.html')
            
            # Create new question
            new_question = DSAQuestion(
                topic_name=topic_name,
                question_name=question_name,
                difficulty_level=difficulty_level,
                question_link=question_link if question_link else None,
                approach1_description=approach1_description,
                approach1_time_complexity=approach1_time_complexity,
                approach2_description=approach2_description if approach2_description else None,
                approach2_time_complexity=approach2_time_complexity if approach2_time_complexity else None,
                approach3_description=approach3_description if approach3_description else None,
                approach3_time_complexity=approach3_time_complexity if approach3_time_complexity else None,
                user_id=current_user.id
            )
            
            db.session.add(new_question)
            db.session.commit()
            
            flash('Question added successfully!', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding question: {str(e)}', 'error')
            return render_template('add_question.html')
    
    return render_template('add_question.html')

@app.route('/view/<int:question_id>')
@login_required
def view_question(question_id):
    """View a specific DSA question"""
    
    question = DSAQuestion.query.filter_by(id=question_id, user_id=current_user.id).first_or_404()
    return render_template('view_question.html', question=question)

@app.route('/edit/<int:question_id>', methods=['GET', 'POST'])
@login_required
def edit_question(question_id):
    """Edit an existing DSA question"""
    
    question = DSAQuestion.query.filter_by(id=question_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        try:
            # Get form data
            question.topic_name = request.form.get('topic_name', '').strip()
            question.question_name = request.form.get('question_name', '').strip()
            question.difficulty_level = request.form.get('difficulty_level')
            question.question_link = request.form.get('question_link', '').strip()
            
            # Approach 1 (required)
            question.approach1_description = request.form.get('approach1_description', '').strip()
            question.approach1_time_complexity = request.form.get('approach1_time_complexity', '').strip()
            
            # Approach 2 (optional)
            approach2_desc = request.form.get('approach2_description', '').strip()
            approach2_time = request.form.get('approach2_time_complexity', '').strip()
            question.approach2_description = approach2_desc if approach2_desc else None
            question.approach2_time_complexity = approach2_time if approach2_time else None
            
            # Approach 3 (optional)
            approach3_desc = request.form.get('approach3_description', '').strip()
            approach3_time = request.form.get('approach3_time_complexity', '').strip()
            question.approach3_description = approach3_desc if approach3_desc else None
            question.approach3_time_complexity = approach3_time if approach3_time else None
            
            # Validation
            if not question.topic_name:
                flash('Topic name is required!', 'error')
                return render_template('edit_question.html', question=question)
            
            if not question.question_name:
                flash('Question name is required!', 'error')
                return render_template('edit_question.html', question=question)
            
            if not question.difficulty_level:
                flash('Difficulty level is required!', 'error')
                return render_template('edit_question.html', question=question)
            
            if not question.approach1_description:
                flash('At least one approach description is required!', 'error')
                return render_template('edit_question.html', question=question)
            
            if not question.approach1_time_complexity:
                flash('Time complexity for approach 1 is required!', 'error')
                return render_template('edit_question.html', question=question)
            
            # Clear question_link if empty
            if not question.question_link:
                question.question_link = None
            
            db.session.commit()
            flash('Question updated successfully!', 'success')
            return redirect(url_for('view_question', question_id=question.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating question: {str(e)}', 'error')
            return render_template('edit_question.html', question=question)
    
    return render_template('edit_question.html', question=question)

@app.route('/delete/<int:question_id>', methods=['POST'])
@login_required
def delete_question(question_id):
    """Delete a DSA question"""
    
    try:
        question = DSAQuestion.query.filter_by(id=question_id, user_id=current_user.id).first_or_404()
        db.session.delete(question)
        db.session.commit()
        flash('Question deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting question: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
