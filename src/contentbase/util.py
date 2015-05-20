from pyramid.threadlocal import manager as threadlocal_manager


def get_root_request():
    if threadlocal_manager.stack:
        return threadlocal_manager.stack[0]['request']
