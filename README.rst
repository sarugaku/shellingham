=============================================
Shellingham: Tool to Detect Surrounding Shell
=============================================

Shellingham detects what shell the current Python executable is running in.


Usage
=====

::

    >>> import shellingham
    >>> shellingham.detect_shell()
    ('bash', '/bin/bash')

``detect_shell`` pokes around the process's running environment to determine
what shell it is run in. It returns a 2-tuple:

* The executable name (without extension on Windows), always lowercased.
* The command used to run the shell.

``ShellDetectionFailure`` is raised if ``detect_shell`` fails to detect the
surrounding shell.
