from instapy import InstaPy
from instapy import smart_run
from instapy import set_workspace


set_workspace(path=None)

session = InstaPy(
    username="abcd",
    password="1234"
)
want_check_browser=False,
with smart_run(session):
    session.set_dont_include(["friend1", "friend2", "friend3"])

    session.like_by_tags(["natgeo"], amount=10)
