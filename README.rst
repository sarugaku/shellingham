=============================================
Shellingham: Tool to Detect Surrounding Shell
=============================================

.. image:: https://img.shields.io/pypi/v/shellingham.svg
    :target: https://pypi.org/project/shellingham/

Shellingham detects what shell the current Python executable is running in.


Usage
=====

::

    >>> import shellingham
    >>> shellingham.detect_shell()
    ('bash', '/bin/bash')

``detect_shell`` pokes around the process's running environment to determine
what shell it is run in. It returns a 2-tuple:

* The shell name, always lowercased.
* The command used to run the shell.

``ShellDetectionFailure`` is raised if ``detect_shell`` fails to detect the
surrounding shell.

Notes
=====

* The shell name is always lowercased.
* On Windows, the shell name is the name of the executable, minus the file exetension.
* Currently the command only contains the executable name on Windows, even if the command is invoked by the full path. This may change in the future.
