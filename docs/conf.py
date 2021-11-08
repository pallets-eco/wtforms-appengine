import os
import sys

from pallets_sphinx_themes import get_version
from pallets_sphinx_themes import ProjectLink

sys.path.insert(0, os.path.abspath(".."))

# -- Project -------------------------------------------------------------------

project = "WTForms-Appengine"

# -- General -------------------------------------------------------------------

master_doc = "index"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "pallets_sphinx_themes",
    "sphinx_issues",
    "sphinxcontrib.log_cabinet",
]
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "WTForms": ("https://wtforms.readthedocs.io/en/stable/", None),
}
copyright = "2021, WTForms Team"
release, version = get_version("WTForms")
exclude_patterns = ["_build"]
pygments_style = "sphinx"

# -- HTML ----------------------------------------------------------------------

html_theme = "werkzeug"
html_context = {
    "project_links": [
        ProjectLink(
            "WTForms documentation", "https://wtforms.readthedocs.io/en/stable/"
        ),
        ProjectLink("PyPI Releases", "https://pypi.org/project/WTForms-Appengine/"),
        ProjectLink("Source Code", "https://github.com/wtforms/wtforms-appengine/"),
        ProjectLink(
            "Discord Chat",
            "https://discord.gg/F65P7Z9",
        ),
        ProjectLink(
            "Issue Tracker", "https://github.com/wtforms/wtforms-appengine/issues/"
        ),
    ]
}
html_sidebars = {
    "index": ["project.html", "localtoc.html", "searchbox.html"],
    "**": ["localtoc.html", "relations.html", "searchbox.html"],
}
singlehtml_sidebars = {"index": ["project.html", "localtoc.html"]}
html_title = f"WTForms Appengine Documentation ({version})"
html_show_sourcelink = False

# -- LATEX ---------------------------------------------------------------------

latex_documents = [
    (
        "index",
        "WTForms-Appengine.tex",
        "WTForms-Appengine Documentation",
        "WTForms Team",
        "manual",
    ),
]
