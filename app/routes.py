from flask import Blueprint, flash, redirect, render_template, request, url_for
from .models import (
    ALLOWED_ENGINES,
    ALLOWED_MODELS,
    ALLOWED_SEVERITIES,
    ALLOWED_YEARS,
    VALID_ENGINE_YEAR_MAP,
    Problem,
    db,
)

bp = Blueprint('main', __name__)


def get_form_options():
    return {
        'models': ALLOWED_MODELS,
        'engines': ALLOWED_ENGINES,
        'years': ALLOWED_YEARS,
        'severities': ALLOWED_SEVERITIES,
    }


def validate_problem_form(form):
    required = ['title', 'model', 'engine', 'model_year', 'category', 'symptoms', 'likely_cause', 'recommended_fix']
    missing = [field for field in required if not form.get(field, '').strip()]
    if missing:
        return 'Fill in all required fields.'

    model = form['model'].strip()
    engine = form['engine'].strip()
    model_year = form['model_year'].strip()
    severity = form.get('severity', 'medium').strip().lower()

    if model not in ALLOWED_MODELS:
        return 'Invalid model selected.'
    if engine not in ALLOWED_ENGINES:
        return 'Invalid engine selected.'
    if model_year not in ALLOWED_YEARS:
        return 'Invalid year selected.'
    if severity not in ALLOWED_SEVERITIES:
        return 'Invalid severity selected.'
    if model_year not in VALID_ENGINE_YEAR_MAP.get(engine, set()):
        return 'That engine and year combination is not valid for this project.'

    return None


@bp.route('/')
def index():
    query = request.args.get('q', '').strip().lower()
    model = request.args.get('model', '').strip()
    engine = request.args.get('engine', '').strip()
    model_year = request.args.get('year', '').strip()
    severity = request.args.get('severity', '').strip()

    severity_order = {
        'high': 0,
        'medium': 1,
        'low': 2,
    }

    problems = Problem.query.all()
    problems = sorted(problems, key=lambda p: severity_order.get(p.severity, 3))

    if query:
        problems = [p for p in problems if query in p.to_search_blob()]
    if model:
        problems = [p for p in problems if p.model == model]
    if engine:
        problems = [p for p in problems if p.engine == engine]
    if model_year:
        problems = [p for p in problems if p.model_year == model_year]
    if severity:
        problems = [p for p in problems if p.severity == severity]

    stats = {
        'total': Problem.query.count(),
        'high': Problem.query.filter_by(severity='high').count(),
        'models': len({p.model for p in Problem.query.all()}),
        'engines': len({p.engine for p in Problem.query.all()}),
    }

    return render_template(
        'index.html',
        problems=problems,
        stats=stats,
        filters={
            'q': request.args.get('q', ''),
            'model': model,
            'engine': engine,
            'year': model_year,
            'severity': severity,
        },
        form_options=get_form_options(),
    )


@bp.route('/problems/<slug>')
def problem_detail(slug):
    problem = Problem.query.filter_by(slug=slug).first_or_404()
    return render_template('problems/detail.html', problem=problem)


@bp.route('/submit', methods=['GET', 'POST'])
def submit_problem():
    form_options = get_form_options()
    if request.method == 'POST':
        error = validate_problem_form(request.form)
        if error:
            flash(error, 'error')
            return render_template('submit.html', form=request.form, form_options=form_options)

        problem = Problem(
            title=request.form['title'].strip(),
            model=request.form['model'].strip(),
            engine=request.form['engine'].strip(),
            model_year=request.form['model_year'].strip(),
            category=request.form['category'].strip(),
            symptoms=request.form['symptoms'].strip(),
            likely_cause=request.form['likely_cause'].strip(),
            recommended_fix=request.form['recommended_fix'].strip(),
            severity=request.form.get('severity', 'medium').strip().lower(),
            author_name=request.form.get('author_name', '').strip() or 'Anonymous',
            source_note=request.form.get('source_note', '').strip() or None,
        )
        problem.ensure_slug()
        db.session.add(problem)
        db.session.commit()
        flash('Problem saved. It is now in the database.', 'success')
        return redirect(url_for('main.problem_detail', slug=problem.slug))

    return render_template('submit.html', form={}, form_options=form_options)
