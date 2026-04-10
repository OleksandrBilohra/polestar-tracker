from flask import Blueprint, flash, redirect, render_template, request, url_for
from .ai_verify import verify_oem_part
from .models import (
    ALLOWED_ENGINES,
    ALLOWED_MODELS,
    ALLOWED_SEVERITIES,
    ALLOWED_YEARS,
    VALID_ENGINE_YEAR_MAP,
    OemPart,
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


# ── OEM Parts ────────────────────────────────────────────────────────────

OEM_CATEGORIES = [
    'Engine', 'Brakes', 'Suspension', 'Drivetrain', 'Exhaust',
    'Turbo', 'Intake', 'ECU', 'Body', 'Interior', 'Electrical',
    'Cooling', 'Fuel', 'Transmission', 'Wheels', 'Steering',
]


@bp.route('/oem-parts')
def oem_parts():
    query = request.args.get('q', '').strip().lower()
    model = request.args.get('model', '').strip()
    category = request.args.get('category', '').strip()

    all_parts = OemPart.query.order_by(OemPart.created_at.desc()).all()

    stats = {
        'total': len(all_parts),
        'verified': sum(1 for p in all_parts if p.ai_verified),
        'models': len({p.model for p in all_parts}),
        'categories': len({p.category for p in all_parts}),
    }

    parts = all_parts

    if query:
        parts = [p for p in parts if query in p.to_search_blob()]
    if model:
        parts = [p for p in parts if p.model == model]
    if category:
        parts = [p for p in parts if p.category == category]

    return render_template(
        'oem_parts.html',
        parts=parts,
        stats=stats,
        filters={
            'q': request.args.get('q', ''),
            'model': model,
            'category': category,
        },
        form_options={
            'models': ALLOWED_MODELS,
            'categories': OEM_CATEGORIES,
        },
    )


@bp.route('/oem-parts/<slug>')
def oem_part_detail(slug):
    part = OemPart.query.filter_by(slug=slug).first_or_404()
    return render_template('oem_parts/detail.html', part=part)


def validate_oem_form(form):
    required = ['part_number', 'part_name', 'description', 'model', 'category']
    missing = [f for f in required if not form.get(f, '').strip()]
    if missing:
        return 'Fill in all required fields.'
    if form['model'].strip() not in ALLOWED_MODELS:
        return 'Invalid model selected.'
    if form['category'].strip() not in OEM_CATEGORIES:
        return 'Invalid category selected.'
    return None


@bp.route('/oem-parts/submit', methods=['GET', 'POST'])
def submit_oem_part():
    form_options = {
        'models': ALLOWED_MODELS,
        'categories': OEM_CATEGORIES,
    }

    if request.method == 'POST':
        error = validate_oem_form(request.form)
        if error:
            flash(error, 'error')
            return render_template('oem_submit.html', form=request.form,
                                   form_options=form_options)

        part_number = request.form['part_number'].strip()
        part_name = request.form['part_name'].strip()
        description = request.form['description'].strip()
        model = request.form['model'].strip()
        category = request.form['category'].strip()

        # AI verification
        result = verify_oem_part(part_number, part_name, description,
                                 model, category)

        part = OemPart(
            part_number=part_number,
            part_name=part_name,
            description=description,
            model=model,
            category=category,
            author_name=request.form.get('author_name', '').strip() or 'Anonymous',
            ai_verified=result['verified'],
            ai_verdict=result['verdict'],
        )
        part.ensure_slug()
        db.session.add(part)
        db.session.commit()

        if result['verified']:
            flash('OEM part saved and verified by AI.', 'success')
        else:
            flash('OEM part saved. AI could not fully verify it — see details.', 'error')

        return redirect(url_for('main.oem_part_detail', slug=part.slug))

    return render_template('oem_submit.html', form={}, form_options=form_options)
