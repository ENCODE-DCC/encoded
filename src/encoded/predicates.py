from pyramid.security import has_permission


def includeme(config):
    config.add_view_predicate('subpath_segments', SubpathSegmentsPredicate)
    config.add_view_predicate('additional_permission', AdditionalPermissionPredicate)


class SubpathSegmentsPredicate(object):
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'subpath_segments = %r' % self.val

    phash = text

    def __call__(self, context, request):
        return len(request.subpath) == self.val


class AdditionalPermissionPredicate(object):
    def __init__(self, val, config):
        self.val = val

    def text(self):
        return 'additional_permission = %r' % self.val

    phash = text

    def __call__(self, context, request):
        return has_permission(self.val, context, request)
