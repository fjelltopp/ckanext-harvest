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
                    if user_obj:
                        context['auth_user_obj'] = user_obj
        except Exception:
            # Intentionally ignore failures when loading user from request
            # so that authorization can safely fall back to CKAN defaults
            pass


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
