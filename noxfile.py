import nox

nox.options.reuse_existing_virtualenvs = True
nox.options.default_venv_backend = "none"


@nox.session
def html(session):
    """Builds the html for the site locally for static rendering."""
    session.run("uv", "sync", "--frozen", "--group", "build", external=True)
    session.run("uv", "run", "quarto", "render", external=True)


@nox.session
def serve(session):
    """Builds the quarto site locally using quarto preview. Opens a local host
    which allows for a live preview that updates as you work."""
    session.run("uv", "sync", "--frozen", "--group", "build", external=True)
    session.run("uv", "run", "quarto", "preview", external=True)
