from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from utils.validators import sanitize
from utils.decorators import login_required, role_required
from services import company_service

bp = Blueprint('companies', __name__, url_prefix='/companies')


@bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required('employer')
def create():
    existing = company_service.get_company_by_employer(session['user_id'])
    if existing:
        flash('لديك شركة بالفعل!', 'error')
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        cn = sanitize(request.form.get('company_name', ''), 100)
        if not cn:
            flash('اسم الشركة مطلوب', 'error')
            return render_template('index_create_company.html', page='create_company')

        company, msg = company_service.create_company(
            employer_id=session['user_id'],
            name=cn,
            description=sanitize(request.form.get('description', ''), 500),
            website=sanitize(request.form.get('website', ''), 200),
            location=sanitize(request.form.get('location', ''), 100),
            owner_name=sanitize(request.form.get('owner_name', ''), 100),
            owner_id_number=sanitize(request.form.get('owner_id', ''), 50)
        )

        if company:
            flash(msg, 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash(msg, 'error')
            return render_template('index_create_company.html', page='create_company')

    return render_template('index_create_company.html', page='create_company')


@bp.route('/edit/<company_id>', methods=['GET', 'POST'])
@login_required
@role_required('employer')
def edit(company_id):
    if not company_service.is_company_owner(session['user_id'], company_id):
        flash('غير مصرح', 'error')
        return redirect(url_for('main.dashboard'))

    from models.company import Company
    company = Company.query.get(company_id)

    if request.method == 'POST':
        company_service.update_company(
            company_id=company_id,
            name=sanitize(request.form.get('company_name', ''), 100),
            description=sanitize(request.form.get('description', ''), 500),
            website=sanitize(request.form.get('website', ''), 200),
            location=sanitize(request.form.get('location', ''), 100)
        )
        flash('تم التحديث', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('index_edit_company.html', page='edit_company', company=company)


@bp.route('/delete/<company_id>')
@login_required
@role_required('employer')
def delete(company_id):
    company_service.delete_company(company_id, session['user_id'])
    flash('تم الحذف', 'success')
    return redirect(url_for('main.dashboard'))


@bp.route('/request-verification')
@login_required
@role_required('employer')
def request_verification():
    success, msg = company_service.request_verification(session['user_id'])
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('main.dashboard'))
