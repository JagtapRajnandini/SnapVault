from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from datetime import datetime

from SnapVault import app, db
from SnapVault.forms.reminder_forms import ReminderForm
from SnapVault.models.reminder import Reminder
from SnapVault.models.document import Document

@app.route('/reminders')
@login_required
def reminder_list():
    # Fetch all reminders for the current user, ordered by due date
    reminders = Reminder.query.filter_by(user_id=current_user.id).order_by(Reminder.due_date.asc()).all()
    
    # Pass today's date so the HTML can color overdue reminders red
    today_date = datetime.now().strftime('%Y-%m-%d')
    return render_template('reminder/list.html', reminders=reminders, today_date=today_date)

@app.route('/reminders/create', methods=['GET', 'POST'])
@login_required
def create_reminder():
    form = ReminderForm()
    
    # Populate the document dropdown with the user's documents
    user_docs = Document.query.filter_by(user_id=current_user.id).all()
    
    # Choice format: (value, label). 0 represents 'No Document'.
    form.document_id.choices = [(0, '--- Do not link a document ---')] + \
                               [(doc.id, doc.original_filename) for doc in user_docs]

    # If the user clicks "Set Reminder" from a specific document page
    prefill_doc_id = request.args.get('doc_id', type=int)
    if request.method == 'GET' and prefill_doc_id:
        form.document_id.data = prefill_doc_id

    if form.validate_on_submit():
        new_reminder = Reminder(
            title=form.title.data,
            due_date=form.due_date.data,
            user_id=current_user.id,
            # Save None in database if '0' (No Document) is selected
            document_id=form.document_id.data if form.document_id.data != 0 else None
        )
        db.session.add(new_reminder)
        db.session.commit()
        flash('Reminder successfully created!', 'success')
        return redirect(url_for('reminder_list'))

    return render_template('reminder/create.html', form=form)

@app.route('/reminders/<int:reminder_id>/complete', methods=['POST'])
@login_required
def complete_reminder(reminder_id):
    reminder = db.session.get(Reminder, reminder_id)
    
    # Security: Ensure reminder exists and belongs to current user
    if not reminder or reminder.user_id != current_user.id:
        flash('Reminder not found.', 'danger')
        return redirect(url_for('reminder_list'))

    reminder.status = 'completed'
    db.session.commit()
    flash('Reminder marked as completed!', 'success')
    return redirect(url_for('reminder_list'))

@app.route('/reminders/<int:reminder_id>/delete', methods=['POST'])
@login_required
def delete_reminder(reminder_id):
    reminder = db.session.get(Reminder, reminder_id)
    
    # Security: Ensure reminder exists and belongs to current user
    if not reminder or reminder.user_id != current_user.id:
        flash('Reminder not found.', 'danger')
        return redirect(url_for('reminder_list'))

    db.session.delete(reminder)
    db.session.commit()
    flash('Reminder deleted successfully.', 'info')
    return redirect(url_for('reminder_list'))