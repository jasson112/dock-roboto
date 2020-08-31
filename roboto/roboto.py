import click
from dotenv import load_dotenv
load_dotenv()
import os
import git
import shutil
import subprocess
import paramiko
from stat import S_ISDIR

class Progress(git.remote.RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        click.echo(click.style('Cloning(%s, %s, %s, %s)' % (op_code, cur_count, max_count, message), fg='yellow'))

class Roboto(object):
    _progressDict={}
    _progressEveryPercent=10
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
    def __init__(self, clone=None, dock=None, media=None, sqlimport=None, copy=None, sqlexport=None):
        for i in range(0,101):
            if i%self._progressEveryPercent==0:
                self._progressDict[str(i)]=""
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
                    subprocess.run(["docker-compose", "-f", "../soho_docker/php/docker-compose.yaml", "up", "-d", "--build"])
                    click.echo(click.style('Done Docker', fg='green'))
                elif dock == "mysql":
                    subprocess.run(["docker-compose", "-f", "../soho_docker/mysql/docker-compose.yaml", "up", "-d", "--build"])
                    click.echo(click.style('Done Docker', fg='green'))
                elif dock == "apache":
                    subprocess.run(["docker-compose", "-f", "../soho_docker/apache/docker-compose.yaml", "up", "-d", "--build"])
                    click.echo(click.style('Done Docker', fg='green'))
                elif dock == "composer":
                    subprocess.run(["docker-compose", "-f", "../soho_docker/php/docker-compose.yaml", "run", "--rm", "cw-php", "composer", "install"])
                    click.echo(click.style('Done Docker', fg='green'))
            if sqlimport:
                if sqlimport == "panama":
                    self.sqlImport("c_", "negocios_masmovilpanama_com")
            if sqlexport:
                if sqlexport:
                    self.sqlExport("c_", "negocios_masmovilpanama_com")
            if media:
                if media == "panama":
                    self.downloadDir(
                        "/var/www/html/flowbusiness.co/sites/negocios.masmovilpanama.com/files", 
                        os.path.join(self._cloneDirs.get("flow"), "sites", "negocios.masmovilpanama.com", "files"), 
                        "10.255.229.14"
                    )
            if copy:
                if copy == "sites":
                    shutil.copy("./drupal-source/sites.php" % (copy), os.path.join(self._cloneDirs.get("flow"), "sites", "settings.php"))
                elif copy == "panama":
                    shutil.copy("./drupal-source/%s/settings.php" % (copy), os.path.join(self._cloneDirs.get("flow"), "sites", "negocios.masmovilpanama.com", "files", "settings.php"))
                    shutil.copy("./drupal-source/services.yml" % (copy), os.path.join(self._cloneDirs.get("flow"), "sites", "negocios.masmovilpanama.com", "files", "services.yml"))
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
        subprocess.run(["cat ../soho_docker/mysql/dump/{prefix}{db}.sql | docker exec -i cw-mysql /usr/bin/mysql -u root --password=root {db}".format(prefix=prefix, db=db)])
        click.echo(click.style('Done Importing', fg='green'))
    
    def sqlExport(self, prefix, db):
        subprocess.run(["docker exec -i cw-mysql mysqldump -uroot -proot --databases {db} > ../soho_docker/mysql/dump/{prefix}{db}.sql".format(prefix=prefix, db=db)])
        click.echo(click.style('Done Exporting', fg='green'))

    def printProgressDecimal(self,x,y):
        if int(100*(int(x)/int(y))) % self._progressEveryPercent ==0 and self._progressDict[str(int(100*(int(x)/int(y))))]=="":
            click.echo(click.style("{}% ({} Transfered(B)/ {} Total File Size(B))".format(str("%.2f" %(100*(int(x)/int(y)))),x,y), fg='blue'))
            self._progressDict[str(int(100*(int(x)/int(y))))]="1"
    
    #todo: change walk to gz zip compress the folder and then uncompress it (more faster)
    def sftp_walk(self, remotepath, sftp, static_path, local_path):
        abspath=remotepath.replace(static_path, local_path)
        path=remotepath
        for f in sftp.listdir_attr(remotepath):
            if S_ISDIR(f.st_mode):
                if not os.path.exists(os.path.join(abspath, f.filename)):
                    os.makedirs(os.path.join(abspath, f.filename))
                self.sftp_walk(os.path.join(remotepath,f.filename), sftp, static_path, local_path)
            else:
                if not os.path.exists(os.path.join(abspath, f.filename)):
                    click.echo(click.style("Found file -> " + os.path.join(abspath, f.filename), fg='yellow'))
                    sftp.get(os.path.join(os.path.join(path,f.filename)), localpath=os.path.join(abspath, f.filename), callback=lambda x,y: self.printProgressDecimal(x,y))
                    click.echo(click.style("100% - Downloaded !", fg='blue'))
                
    def downloadDir(self, remote, local, host):
        paramiko.util.log_to_file('/tmp/paramiko.log')
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, port=22, username=self._credentials.get("ssh")["user"], password="valy9enWnntri$ne")
        sftp = ssh.open_sftp()
        self.sftp_walk(remote, sftp, remote, local)


@click.group(invoke_without_command=True)
@click.option('-c', '--clone', "clone", type=str)
@click.option('-d', '--dock', "dock", type=str)
@click.option('-m', '--media', "media", type=str)
@click.option('-sqli', '--sqlimport', "sqlimport", type=str)
@click.option('-cp', '--copy', "copy", type=str)
@click.option('-sqle', '--sqlexport', "sqlexport", type=str)
@click.pass_context
def cli(ctx, clone, dock, media, sqlimport, copy, sqlexport):
    ctx.obj = Roboto(clone=clone, dock=dock, media=media, copy=copy, sqlexport=sqlexport)
    