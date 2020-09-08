import click
from dotenv import load_dotenv
load_dotenv()
import os
import git
import shutil
import subprocess
import paramiko
from stat import S_ISDIR
import tarfile
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import gzip
from tqdm import tqdm
from io import BytesIO
import sys

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
    def __init__(self, clone=None, dock=None, media=None, sqlimport=None, copy=None, sqlexport=None, flush=None):
        for i in range(0,101):
            if i%self._progressEveryPercent==0:
                self._progressDict[str(i)]=""
        if os.getenv("GIT_USER") and os.getenv("GIT_PASS") and os.getenv("SSH_USER") and os.getenv("SSH_PASS"):
            #click.echo(click.style('All rigthooo !', fg='green'))
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
                    path = "%s/sites/flowbusiness.co.trinidad-and-tobago" % (self._cloneDirs.get("flow"))
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
                        "/var/www/html/flowbusiness.co/sites/negocios.masmovilpanama.com", 
                        os.path.join(self._cloneDirs.get("flow"), "sites", "negocios.masmovilpanama.com"), 
                        "10.255.229.14",
                        "files"
                    )
                elif media == "trinidad":
                    self.downloadDir(
                        "/var/www/html/dev.flowbusiness.co/sites/flowbusiness.co.trinidad-and-tobago", 
                        os.path.join(self._cloneDirs.get("flow"), "sites", "flowbusiness.co.trinidad-and-tobago"), 
                        "10.255.229.13",
                        "files"
                    )
            if copy:
                if copy == "sites":
                    shutil.copy("./drupal-source/sites.php", os.path.join(self._cloneDirs.get("flow"), "sites", "settings.php"))
                elif copy == "panama":
                    shutil.copy("./drupal-source/%s/settings.php" % (copy), os.path.join(self._cloneDirs.get("flow"), "sites", "negocios.masmovilpanama.com", "settings.php"))
                    shutil.copy("./drupal-source/services.yml", os.path.join(self._cloneDirs.get("flow"), "sites", "negocios.masmovilpanama.com", "services.yml"))
                elif copy == "trinidad":
                    shutil.copy("./drupal-source/%s/settings.php" % (copy), os.path.join(self._cloneDirs.get("flow"), "sites", "flowbusiness.co.trinidad-and-tobago", "settings.php"))
                    shutil.copy("./drupal-source/services.yml", os.path.join(self._cloneDirs.get("flow"), "sites", "flowbusiness.co.trinidad-and-tobago", "services.yml"))
            if flush:
                if flush == "panama":
                    #docker-compose -f ../soho_docker/php/docker-compose.yaml run --rm  cw-php vendor/bin/drush --uri=flowpanama.com  cache-rebuild -vvv
                    subprocess.run(["docker-compose", "-f", "../soho_docker/apache/docker-compose.yaml", "run", "--rm", "cw-php", "vendor/bin/drush --uri=flowpanama.com  cache-rebuild -vvv"])
                    click.echo(click.style('Done Flush in panama', fg='green'))
                if flush == "trinidad":
                    subprocess.run(["docker-compose", "-f", "../soho_docker/apache/docker-compose.yaml", "run", "--rm", "cw-php", "vendor/bin/drush --uri=flowpanama.com  cache-rebuild -vvv"])
                    click.echo(click.style('Done Flush in panama', fg='green'))
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
                
    def downloadDir(self, remote, local, host, files):
        paramiko.util.log_to_file('/tmp/paramiko.log')
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, port=22, username=self._credentials.get("ssh")["user"], password="valy9enWnntri$ne")
        sftp = ssh.open_sftp()
        members = None
        cmd = 'cd {remote} && tar cf - "{files}" --exclude="css" --exclude="js" --exclude="php" --strip-components=5 2>/dev/null | gzip -9 2>/dev/null'.format(remote=remote, files=files)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        #<TRICK
        #print(cmd)
        print(os.path.expanduser("~/Documents/dev/dock-roboto/{local}".format(local=local)))
        sys.stdout = open("{local}/temp.tar.gz".format(local=local), 'wb')
        sys.stdout.write(stdout.read())
        sys.stdout.close()
        
        """
        Extracts `tar_file` and puts the `members` to `path`.
        If members is None, all members on `tar_file` will be extracted.
        """
        tar = tarfile.open("{local}/temp.tar.gz".format(local=local), mode="r:gz")
        if members is None:
            members = tar.getmembers()
        # with progress bar
        # set the progress bar
        progress = tqdm(members)
        for member in progress:
            tar.extract(member, path=local)
            # set the progress description of the progress bar
            progress.set_description(f"Extracting {member.name}")
        # or use this
        # tar.extractall(members=members, path=path)
        # close the file
        tar.close()
        


@click.group(invoke_without_command=True)
@click.option('-c', '--clone', "clone", type=str)
@click.option('-d', '--dock', "dock", type=str)
@click.option('-m', '--media', "media", type=str)
@click.option('-sqli', '--sqlimport', "sqlimport", type=str)
@click.option('-cp', '--copy', "copy", type=str)
@click.option('-sqle', '--sqlexport', "sqlexport", type=str)
@click.option('-f', '--flush', "flush", type=str)
@click.pass_context
def cli(ctx, clone, dock, media, sqlimport, copy, sqlexport, flush):
    ctx.obj = Roboto(clone=clone, dock=dock, media=media, copy=copy, sqlexport=sqlexport, flush=flush)
    