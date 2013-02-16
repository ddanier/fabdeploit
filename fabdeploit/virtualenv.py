from __future__ import absolute_import
import fabric.api as fab
import posixpath

# IDEA:
# Initialize a virtualenv using some REQUIREMENTS file. Then initialize a
# git repository in it. Create tags for every release made using
# "release/$COMMIT_SHA1" as tag name. This way we can revert to old versions
# inside the virtualenv as well.


def _env_path(command='python2'):
    if 'deploy_env_path' in fab.env:
        return posixpath.join(fab.env.deploy_env_path, 'bin', command)
    else:
        return command


def create_commit(message=None, tag=None):
    import datetime
    
    assert 'deploy_env_path' in fab.env
    
    if not getattr(fab.env, 'deploy_env_history', False):
        return
    
    if message is None:
        message = datetime.datetime.now().isoformat()
    with fab.cd(fab.env.deploy_env_path):
        # (re) initialize
        fab.run('git init')
        # addremove everything
        fab.run('git add -A')
        fab.run('git ls-files --deleted -z | xargs -r -0 git rm')
        # create commit
        fab.run('git commit -m "%s"' % message)
        if tag:
            fab.run('git tag "%s"' % tag)


def init(force=False):
    from fabric.contrib import files
    
    assert 'deploy_env_path' in fab.env
    
    if not force and files.exists(fab.env.deploy_env_path):
        return
    
    download_path = posixpath.join(fab.env.deploy_env_path, 'download')
    download_virtualenv_bin = posixpath.join(download_path, 'virtualenv.py')
    fab.run('mkdir -p "%s"' % download_path)
    fab.run('wget https://raw.github.com/pypa/virtualenv/master/virtualenv.py -O "%s"' % download_virtualenv_bin)
    fab.run('python2 "%s" --clear --no-site-packages "%s"' % (
        download_virtualenv_bin,
        fab.env.deploy_env_path,
    ))


def update_deps():
    import datetime
    
    assert 'deploy_env_path' in fab.env
    assert 'deploy_env_requirements' in fab.env
    
    fab.run('%s install -r "%s" -U' % (
        _env_path('pip'),
        fab.env.deploy_env_requirements,
    ))


def switch(commit):
    assert 'deploy_env_path' in fab.env
    
    if not getattr(fab.env, 'deploy_env_history', False):
        fab.abort('Cannot switch to older version, git is not enabled for virtualenv (see env.deploy_env_history)')
    
    with fab.cd(fab.env.deploy_env_path):
        fab.run('git reset --hard "%s"' % commit)

