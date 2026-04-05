from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from slugify import slugify


db = SQLAlchemy()

ALLOWED_MODELS = ['S60 Polestar', 'V60 Polestar']
ALLOWED_ENGINES = ['3.0 T6', '2.0 T6 Drive-E']
ALLOWED_YEARS = ['2014', '2015', '2016', '2017', '2018']
ALLOWED_SEVERITIES = ['low', 'medium', 'high']

VALID_ENGINE_YEAR_MAP = {
    '3.0 T6': {'2014', '2015', '2016'},
    '2.0 T6 Drive-E': {'2016', '2017', '2018'},
}


class Problem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), nullable=False)
    slug = db.Column(db.String(190), unique=True, nullable=False)
    model = db.Column(db.String(80), nullable=False)
    engine = db.Column(db.String(80), nullable=False)
    model_year = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    likely_cause = db.Column(db.Text, nullable=False)
    recommended_fix = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20), nullable=False, default='medium')
    author_name = db.Column(db.String(120), nullable=True)
    source_note = db.Column(db.String(160), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def ensure_slug(self):
        base = slugify(f'{self.model}-{self.model_year}-{self.title}')[:170] or 'problem'
        slug = base
        counter = 2
        while Problem.query.filter(Problem.slug == slug, Problem.id != self.id).first():
            slug = f'{base}-{counter}'
            counter += 1
        self.slug = slug

    def to_search_blob(self):
        return ' '.join([
            self.title,
            self.model,
            self.engine,
            self.model_year,
            self.category,
            self.symptoms,
            self.likely_cause,
            self.recommended_fix,
            self.author_name or '',
            self.source_note or '',
        ]).lower()
