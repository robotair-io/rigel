import nox


# Run unit tests and perform test coverage.
@nox.session(python=["3.8", "3.9"])
def tests(session: nox.sessions.Session) -> None:
    """
    Installs Poetry, runs the project's tests using Pytest and reports test coverage
    statistics using Coverage.

    Args:
        session (nox.sessions.Session): Used to manage the lifecycle of the test
            environment.

    """
    session.install("poetry")
    session.run("poetry", "install")
    session.run("coverage", "run", "-m", "pytest")
    session.run("coverage", "report")


# Run flake8 linter.
@nox.session
def lint(session: nox.sessions.Session) -> None:
    """
    Installs Poetry, a Python package manager, and uses it to install dependencies.
    Then, it runs Flake8, a static code analysis tool, on the current directory
    (.). This ensures that the code is free from syntax errors and follows PEP 8
    style guidelines.

    Args:
        session (nox.sessions.Session): Used to interact with the Nox testing tool,
            which allows for running tests and other commands within the context
            of a session.

    """
    session.install("poetry")
    session.run("poetry", "install")
    session.run("flake8", ".")


# # Run mypy type checker.
@nox.session
def typing(session: nox.sessions.Session) -> None:
    """
    Sets up a Poetry project by installing the package manager and then installs
    dependencies using Poetry. Additionally, it runs MyPy type checker to check
    for type errors in the project's source code.

    Args:
        session (nox.sessions.Session): An instance that represents the current
            execution context for the script.

    """
    session.install("poetry")
    session.run("poetry", "install")
    session.run("mypy", ".")
