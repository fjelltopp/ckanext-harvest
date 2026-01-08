from ckan.plugins import toolkit as pt
from ckanext.harvest.logic.auth import user_is_sysadmin, load_user_from_flask_request
import ckan.logic.auth.create as create_auth


def package_create(context, data_dict):
    """
    Authorization for creating packages (harvest and regular types).

    In CKAN 2.11, this auth function is called before showing the creation form.
    When viewing forms (empty data_dict), allow sysadmins to proceed.
    """
    # Load user from Flask request if not already in context (CKAN 2.11 Flask issue)
    load_user_from_flask_request(context)

    package_type = data_dict.get('type', '')

    # Check if user is sysadmin
    try:
        is_sysadmin = user_is_sysadmin(context)

        # For harvest packages OR empty data_dict (form viewing), allow sysadmins
        # NOTE: In CKAN 2.11, when rendering the harvest creation form (GET on /harvest/new),
        #       package_create can be called with an empty data_dict. In this specific "view form"
        #       case, we rely on an empty data_dict to grant sysadmins access to the form.
        #       This is a Flask-specific behavior where auth checks occur before form rendering.
        if is_sysadmin and (package_type == 'harvest' or not data_dict):
            return {'success': True}
    except Exception:
        # Intentionally ignore failures in sysadmin check so that authorization
        # can fall back to CKAN's default package_create logic below
        pass

    # For non-sysadmins or non-harvest packages, use CKAN's default auth
    return create_auth.package_create(context, data_dict)


def harvest_source_create(context, data_dict):
    '''
        Authorization check for harvest source creation

        It forwards the checks to package_create, which will check for
        organization membership, whether if sysadmin, etc according to the
        instance configuration.
    '''
    user = context.get('user')
    try:
        pt.check_access('package_create', context, data_dict)
        return {'success': True}
    except pt.NotAuthorized:
        return {'success': False,
                'msg': pt._('User {0} not authorized to create harvest sources').format(user)}


def harvest_job_create(context, data_dict):
    '''
        Authorization check for harvest job creation

        It forwards the checks to package_update, ie the user can only create
        new jobs if she is allowed to edit the harvest source dataset.
    '''
    model = context['model']
    source_id = data_dict['source_id']

    pkg = model.Package.get(source_id)
    if not pkg:
        raise pt.ObjectNotFound(pt._('Harvest source not found'))

    context['package'] = pkg
    try:
        # Pass the package id to package_update for authorization check
        pt.check_access('package_update', context, {'id': pkg.id})
        return {'success': True}
    except pt.NotAuthorized:
        return {'success': False,
                'msg': pt._('User not authorized to create a job for source {0}').format(source_id)}


def harvest_job_create_all(context, data_dict):
    '''
        Authorization check for creating new jobs for all sources

        Only sysadmins can do it
    '''
    if not user_is_sysadmin(context):
        return {'success': False, 'msg': pt._('Only sysadmins can create harvest jobs for all sources')}
    else:
        return {'success': True}


def harvest_object_create(context, data_dict):
    """
        Auth check for creating a harvest object

        only the sysadmins can create harvest objects
    """
    # sysadmins can run all actions if we've got to this point we're not a sysadmin
    return {'success': False, 'msg': pt._('Only the sysadmins can create harvest objects')}
