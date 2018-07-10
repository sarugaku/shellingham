1.2.3 (2018-07-10)
=======================

Bug Fixes
---------

- Check a process’s argument list is valid before peeking into it. This works
  around a Heisenbug in VS Code, where a process read from ``/proc`` may
  contain an empty argument list.


1.2.2 (2018-07-09)
==================

Features
--------

- Support BSD-style ``/proc`` format.  `#4
  <https://github.com/sarugaku/shellingham/issues/4>`_


Bug Fixes
---------

- Better ``ps`` output decoding to fix compatibility.  `#7
  <https://github.com/sarugaku/shellingham/issues/7>`_


1.2.1 (2018-07-04)
==================

Bug Fixes
---------

- Fix login shell detection if it is ``chsh``-ed to point to an absolute path.
  `#6 <https://github.com/sarugaku/shellingham/issues/6>`_


1.2.0 (2018-07-04)
==================

Features
--------

- Prefer the ``/proc``-based approach on POSIX whenever it is likely to work.
  `#5 <https://github.com/sarugaku/shellingham/issues/5>`_


1.1.0 (2018-06-19)
==================

Features
--------

- Use ``/proc`` on Linux to build process tree. This is more reliable than
  ``ps``, which may not be available on a bare installation.  `#3
  <https://github.com/sarugaku/shellingham/issues/3>`_


1.0.1 (2018-06-19)
==================

Bug Fixes
---------

- Fix POSIX usage on Python 2 by providing more compatible arguments to parse
  ``ps`` results. Thanks to @glehmann for the patch.  `#2
  <https://github.com/sarugaku/shellingham/issues/2>`_


1.0.0.dev1 (2018-06-15)
=======================

Bug Fixes
---------

- Prevent the lookup from exploding when running in non-hierarchical process
  structure. (1-b2e9bef5)


1.0.0.dev0 (2018-06-14)
=======================

Initial release.
