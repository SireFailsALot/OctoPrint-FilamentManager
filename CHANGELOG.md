## CHANGE LOG

## VERSION 0.6.0 (7/24/2020)

* Added the ability for the server to pessamistaccaly reconnect to the external database.
* Added the ability to add notes to spool profiles, which are displayed in the side bar.
* Fixed FilamentManager.execute_script, which would throw exceptions on execution due to internally containing a blank string.
* Updated to a newer version of SQLAlchemy, which now supports pre_pool_ping.
* Added Python 3.X support.
* Fixed gulpfile.js so that it now works with gulp version 4 and node.js 12
* Changed line endings to unix style
