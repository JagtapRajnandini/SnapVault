from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

class ReminderForm(FlaskForm):
    title = StringField(
        'Reminder Title',
        validators=[
            DataRequired(message="Please provide a title."),
            Length(max=200, message="Title cannot exceed 200 characters.")
        ],
        description="E.g., Pay Electricity Bill, Renew Passport"
    )

    due_date = DateField(
        'Due Date',
        format='%Y-%m-%d',
        validators=[DataRequired(message="Please select a valid date.")],
    )

    # This field will be dynamically populated in the route
    # with the user's uploaded documents.
    document_id = SelectField(
        'Link to Document (Optional)',
        coerce=int,
        choices=[]
    )

    submit = SubmitField('Set Reminder')