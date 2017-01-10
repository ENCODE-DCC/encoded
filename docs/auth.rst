================================
Authentication and authorization
================================

Background reading: `Pyramid's security system`_.

.. _Pyramid's security system: http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/security.html

I extend Pyramid's built in ACL based security system with my pyramid_localroles_ plugin so we can map permissions to roles (e.g. 'role.lab_submitter') rather than directly to users.

.. _pyramid_localroles: https://pypi.python.org/pypi/pyramid_localroles/

For more on roles and local roles see:

* http://docs.zope.org/zope2/zope2book/Security.html#different-levels-of-access-with-roles
* http://www.sixfeetup.com/blog/basic-roles-and-permissions-in-plone
* https://www.packtpub.com/books/content/plone-4-development-understanding-zope-security

Authentication
==============

An authentication policy identifies who you are, returning a user id.
We use pyramid_multiauth to extract authentication from any of `Persona <https://www.persona.org/>`_, session cookies, or HTTP basic auth (access keys).

Authorization
=============

From the authenticated user id, the groupfinder in authorization.py_ maps the user id to a number of "principals", user or group identifiers.
We lookup the user object and add groups based on the properties:

* groups [<string>..] - global groups like 'admin'. Generates: `group.admin`.
* submits_for: [lab..] - allow editing based on object.lab property. Generates: `submits_for.<lab-uuid>`.
* viewing_groups: [<string..>] - allow viewing of in progress data based on object.award.viewing_group (ENCODE3, ENCODE4, GGR, REMC.) Generates: `viewing_group.ENCODE`.

.. _authorization.py: ../src/encoded/authorization.py

Views are protected by permissions (`view`, `edit`, etc.)

When you PUT to /experiment/ENCSR123ABC/ then Pyramid will traverse to the experiment object (see: `Location aware resources`_) and lookup a view for to PUT which is protected with the `edit` permission.

.. _Location aware resources: http://docs.pylonsproject.org/projects/pyramid/en/latest/narr/resources.html#location-aware

At this point my pyramid_localroles plugin steps in and extends the authenticated principals passed to the ACLAuthorizationPolicy (the global groups that apply across the whole site) with location aware local roles such as `role.lab_submitter` and `role.viewing_group_member` by reference to the `__ac_local_roles__` method (base.py_) of the context object which returns a mapping based on the context object's 'lab' and award property, e.g::

  {
    'submits_for.<context-lab-uuid>': ['role.lab_submitter'],
    'viewing_group.<context-award-viewing_group>'': ['role.viewing_group_member'],
  }

The ACL authorization policy will then lookup the Access Control List on the experiment object (the 'context') by looking at its `__acl__` property/method, and then the `__acl__` property/methods of its parents (the /experiments collection and the root object.)
We define an `__acl__` method on the EncodedRoot object (root.py_), Collection and Item objects (base.py_.)
The `__acl__` method for an Item returns a different ACL list depending on the object's 'status'.
This way we allow lab submitters to edit their own 'in progress' objects but not 'released' objects.

Schema-Based Restrictions
=========================

If you specify in the JSON schema for a property of an an object:  "permissions": "import-items" then only admins may change these values independend of submitter.


.. _base.py: ../src/encoded/types/base.py
.. _root.py: ../src/encoded/root.py

Permissions
===========

* add
* add_unvalidated (admin)
* audit - view audits on an individual content item
* edit
* edit_unvalidated (admin)
* expand (system)
* forms - who can see forms
* impersonate (admin)
* import_items (admin)
* index (system)
* list
* search
* search_audit - global permission to see audits in search results
* submit_for_any (admin)
* view
* view_details - protection of user contact information
* view_raw (admin)
* visible_for_edit - hiding deleted child objects from edit

This gnu grep expression will extract a list of permissions (brew tap homebrew/dupes; brew install grep)::

    $ ggrep --no-filename -roP "(?<=permission[=(]['\"])[^'\"]+" src/ | sort | uniq
