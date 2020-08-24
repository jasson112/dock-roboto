import click
from dotenv import load_dotenv
load_dotenv()
import os
import git
import shutil
import subprocess

class Progress(git.remote.RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        click.echo(click.style('Cloning(%s, %s, %s, %s)' % (op_code, cur_count, max_count, message), fg='yellow'))

class Roboto(object):
    _credentials = {
        "ssh": {
            "user": None,
            "pass": None
        },
        "git": {
            "user": None,
            "pass": None
        }
    }
    _cloneDirs = {
        "flow": "./flowbusiness_co",
        "cwnet": "./cwnetworks.com",
        "bus": "./cwbusiness.com",
    }
    def __init__(self, clone=None, dock=None):
        if os.getenv("GIT_USER") and os.getenv("GIT_PASS") and os.getenv("SSH_USER") and os.getenv("SSH_PASS"):
            click.echo(click.style('All rigthooo !', fg='green'))
            self._credentials.get("git")["user"] = os.getenv("GIT_USER")
            self._credentials.get("git")["pass"] = os.getenv("GIT_PASS")
            self._credentials.get("ssh")["user"] = os.getenv("SSH_USER")
            self._credentials.get("ssh")["pass"] = os.getenv("SSH_PASS")
            self._repos = {
                "flow":{
                    "main": "http://%s:%s@bssstash.corp-it.cc:7990/scm/fb/flowbusiness_co.git" % (self._credentials.get("git")["user"], self._credentials.get("git")["pass"]),
                    "bb": "http://%s:%s@bssstash.corp-it.cc:7990/scm/fb/sites_flowbusiness_bb.git" % (self._credentials.get("git")["user"], self._credentials.get("git")["pass"]),
                    "panama": "http://%s:%s@bssstash.corp-it.cc:7990/scm/fb/sites_masmovilpanama_negocios.git" % (self._credentials.get("git")["user"], self._credentials.get("git")["pass"]),
                    "trinidad": "http://%s:%s@bssstash.corp-it.cc:7990/scm/fb/sites_flowbusiness_tt.git" % (self._credentials.get("git")["user"], self._credentials.get("git")["pass"]),
                },
                "cw": {
                    "net": "http://%s:%s@bssstash.corp-it.cc:7990/scm/cwnet/core.git" % (self._credentials.get("git")["user"], self._credentials.get("git")["pass"]),
                    "bus": "http://%s:%s@bssstash.corp-it.cc:7990/scm/cwcbus/core.git" % (self._credentials.get("git")["user"], self._credentials.get("git")["pass"]),
                }
            }
            if clone:
                click.echo(click.style('Cloning %s' % (clone), fg='green'))
                if clone == "panama":
                    url = self._repos.get("flow")[clone]
                    path = "%s/sites/negocios.masmovilpanama.com" % (self._cloneDirs.get("flow"))
                    click.echo(click.style('clone url %s' % (url), fg='green'))
                    self.gitClone(url, path)
                elif clone == "main":
                    url = self._repos.get("flow")[clone]
                    path = "%s" % (self._cloneDirs.get("flow"))
                    click.echo(click.style('clone url %s' % (url), fg='green'))
                    self.gitClone(url, path)
                elif clone == "bb":
                    url = self._repos.get("flow")[clone]
                    path = "%s/sites/flowbusiness.co.barbados" % (self._cloneDirs.get("flow"))
                    click.echo(click.style('clone url %s' % (url), fg='green'))
                    self.gitClone(url, path)
                elif clone == "trinidad":
                    url = self._repos.get("flow")[clone]
                    path = "%s/sites/flowbusiness.co.trinidad" % (self._cloneDirs.get("flow"))
                    click.echo(click.style('clone url %s' % (url), fg='green'))
                    self.gitClone(url, path)
                elif clone == "net":
                    url = self._repos.get("cw")[clone]
                    path = "%s" % (self._cloneDirs.get("cwnet"))
                    click.echo(click.style('clone url %s' % (url), fg='green'))
                    self.gitClone(url, path)
                elif clone == "bus":
                    url = self._repos.get("cw")[clone]
                    path = "%s" % (self._cloneDirs.get("bus"))
                    click.echo(click.style('clone url %s' % (url), fg='green'))
                    self.gitClone(url, path)
            if dock:
                if dock == "php":
                    command = subprocess.run(["docker-compose", "-f", "../soho_docker/php/docker-compose.yaml", "up", "-d", "--build"])
                    click.echo(click.style('Done Docker', fg='green'))
                elif dock == "mysql":
                    command = subprocess.run(["docker-compose", "-f", "../soho_docker/mysql/docker-compose.yaml", "up", "-d", "--build"])
                    click.echo(click.style('Done Docker', fg='green'))
                elif dock == "apache":
                    command = subprocess.run(["docker-compose", "-f", "../soho_docker/apache/docker-compose.yaml", "up", "-d", "--build"])
                    click.echo(click.style('Done Docker', fg='green'))
                elif dock == "composer":
                    command = subprocess.run(["docker-compose", "-f", "../soho_docker/php/docker-compose.yaml", "run", "--rm", "cw-php", "php", "composer.phar", "install"])
                    click.echo(click.style('Done Docker', fg='green'))
            if sqlimport:
                if sqlimport == "panama":
                    self.sqlImport("c_", "negocios_masmovilpanama_com")
        else:
            click.echo(click.style('Environment variables not found. Check your .env file', fg='red'))

    def gitClone(self, cloneUrl, clonePath):
        if not os.path.exists(clonePath):
            os.makedirs(clonePath)
        else:
            shutil.rmtree(clonePath)
        git.Repo.clone_from(cloneUrl, clonePath, progress=Progress())
        click.echo(click.style('Done cloning !', fg='green'))
    
    def sqlImport(self, prefix, db):
        command = subprocess.run(["cat ../soho_docker/mysql/dump/{prefix}{db}.sql | docker exec -i cw-mysql /usr/bin/mysql -u root --password=root {db}".format(prefix=prefix, db=db)])
        click.echo(click.style('Done Docker', fg='green'))

@click.group(invoke_without_command=True)
@click.option('-c', '--clone', "clone", type=str)
@click.option('-d', '--dock', "dock", type=str)
@click.pass_context
def cli(ctx, clone, dock):
    ctx.obj = Roboto(clone=clone, dock=dock)
    