import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.usefixtures('workbook')

scenarios(
    'forms.feature',
    'page.feature',
)


@pytest.fixture
def browser(request, browser_instance_getter, base_url):
    admin_browser = browser_instance_getter(request, browser)
    admin_browser.visit(base_url)  # need to be on domain to set cookie
    admin_browser.cookies.add({'REMOTE_USER': 'TEST'})
    return admin_browser
