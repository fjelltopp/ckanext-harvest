from ckan.plugins import toolkit as pt
from ckanext.harvest import model as harvest_model

try:
    from flask import request
except ImportError:
    # Flask not available (shouldn't happen in CKAN 2.11+)
    request = None


def user_is_sysadmin(context):
    '''
        Checks if the user defined in the context is a sysadmin

        rtype: boolean
    '''
    model = context['model']
    user = context['user']
    user_obj = model.User.get(user)
    if not user_obj:
        raise pt.Objectpt.ObjectNotFound('User {0} not found').format(user)

    return user_obj.sysadmin


def load_user_from_flask_request(context):
    """
    Load user from Flask request environ into context if not already present.

    In CKAN 2.11, when accessing harvest forms, authorization checks happen
    before the user is loaded into context, even though REMOTE_USER is set
    in the Flask request environ. This helper ensures the user is loaded
    for proper authorization checks.

    Args:
        context: CKAN context dict

    Returns:
        None (modifies context in-place)
    """
    if not request:
        return

    user = context.get('user', '')
    if not user:
        try:
            user = request.environ.get('REMOTE_USER', '')
            if user:
                context['user'] = user
                # Load user object into context for sysadmin checks
                model = context.get('model')
                if model:
                    user_obj = model.User.get(user)
                    # Mirror CKAN's own _get_user contract: only inject active
                    # users so a deleted/blocked account whose name lingers in
                    # REMOTE_USER (e.g. from a still-valid session cookie) does
                    # not retain auth privileges.
                    if user_obj and getattr(user_obj, 'state', None) == 'active':
                        context['auth_user_obj'] = user_obj
        except Exception:
            # Intentionally ignore failures when loading user from request
            # so that authorization can safely fall back to CKAN defaults
            pass


def is_harvest_form_view():
    """
    True only for GET requests serving the harvest creation/edit forms.

    Used to safely identify the "form view" case in CKAN 2.11 where
    package_create/package_update auth fires before the form renders with
    a sparse data_dict. Anchored on the request path so unrelated callers
    that happen to pass an empty data_dict do not bypass auth.
    """
    if not request:
        return False
    try:
        if request.method != 'GET':
            return False
        from ckanext.harvest import utils
        path = (request.path or '').rstrip('/')
        prefix = '/{0}/'.format(utils.DATASET_TYPE_NAME)
        return path.endswith('/{0}/new'.format(utils.DATASET_TYPE_NAME)) \
            or (prefix + 'edit/') in (path + '/')
    except Exception:
        return False


def _get_object(context, data_dict, name, class_name):
    '''
        return the named item if in the data_dict, or get it from
        model.class_name
    '''
    if name not in context:
        id = data_dict.get('id', None)
        obj = getattr(harvest_model, class_name).get(id)
        if not obj:
            raise pt.ObjectNotFound
    else:
        obj = context[name]
    return obj


def get_source_object(context, data_dict={}):
    return _get_object(context, data_dict, 'source', 'HarvestSource')


def get_job_object(context, data_dict={}):
    return _get_object(context, data_dict, 'job', 'HarvestJob')


def get_obj_object(context, data_dict={}):
    return _get_object(context, data_dict, 'obj', 'HarvestObject')
