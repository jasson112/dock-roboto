import re
import yaml
from pyngrok import ngrok
from atlassian import Bamboo
import sys
from io import BytesIO
from tqdm import tqdm
import gzip
import tarfile
from stat import S_ISDIR
import paramiko
import subprocess
import shutil
import git
import os
import click
import requests
from dotenv import load_dotenv
load_dotenv()
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class Progress(git.remote.RemoteProgress):
    def update(self, op_code, cur_count, max_count=None, message=''):
        click.echo(click.style('Cloning(%s, %s, %s, %s)' % (op_code, cur_count, max_count, message), fg='yellow'))


class Roboto(object):
    _progressDict = {}
    _progressEveryPercent = 10
    _credentials = {
        "ssh": {
            "user": None,
            "pass": None
        },
        "git": {
            "user": None,
            "pass": None
        },
        "git_bucket": {
            "user": None,
            "pass": None
        },
        "atlassian": {
            "user": None,
            "pass": None,
            "url": "https://bamboo-qa.cwc-apps.com/"
        },
        "rok": {
            "api": None
        }
    }
    _cloneDirs = {
        "flowb": "./flow-business",
        "flow": "./flowbusiness_co",
        "cwnet": "./cwnetworks.com",
        "bus": "./cwbusiness.com",
    }

    def __init__(self, clone=None, dock=None, media=None, sqlimport=None, copy=None, sqlexport=None, flush=None, path=None, bam=None, action=None, rok=None):
        for i in range(0, 101):
            if i % self._progressEveryPercent == 0:
                self._progressDict[str(i)] = ""
        if os.getenv("GIT_USER") and os.getenv("GIT_PASS") and os.getenv("SSH_USER") and os.getenv("SSH_PASS"):
            # click.echo(click.style('All rigthooo !', fg='green'))
            self._credentials.get("atlassian")[
                "user"] = os.getenv("ATLASSIAN_USER")
            self._credentials.get("atlassian")[
                "pass"] = os.getenv("ATLASSIAN_PASS")
            self._credentials.get("rok")["api"] = os.getenv("ROK_API")
            self._credentials.get("git")["user"] = os.getenv("GIT_USER")
            self._credentials.get("git")["pass"] = os.getenv("GIT_PASS")
            self._credentials.get("git_bucket")["user"] = os.getenv("GIT_BUCKET_USER")
            self._credentials.get("git_bucket")["pass"] = os.getenv("GIT_BUCKET_PASS")
            self._credentials.get("ssh")["user"] = os.getenv("SSH_USER")
            self._credentials.get("ssh")["pass"] = os.getenv("SSH_PASS")
            self._repos = {
                "flow": {
                    "main": "http://%s:%s@bssstash.corp-it.cc:7990/scm/fb/flowbusiness_co.git" % (self._credentials.get("git")["user"], self._credentials.get("git")["pass"]),
                    "bb": "http://%s:%s@bssstash.corp-it.cc:7990/scm/fb/sites_flowbusiness_bb.git" % (self._credentials.get("git")["user"], self._credentials.get("git")["pass"]),
                    "panama": "http://%s:%s@bssstash.corp-it.cc:7990/scm/fb/sites_masmovilpanama_negocios.git" % (self._credentials.get("git")["user"], self._credentials.get("git")["pass"]),
                    "trinidad": "http://%s:%s@bssstash.corp-it.cc:7990/scm/fb/sites_flowbusiness_tt.git" % (self._credentials.get("git")["user"], self._credentials.get("git")["pass"]),
                    "jamaica": "http://%s:%s@bssstash.corp-it.cc:7990/scm/fb/sites_flowbusiness_jm.git" % (self._credentials.get("git")["user"], self._credentials.get("git")["pass"]),
                    "flow": "https://%s:%s@bitbucket.cwc-apps.com/scm/fb/flow-business.git" % (self._credentials.get("git_bucket")["user"], self._credentials.get("git_bucket")["pass"])
                },
                "cw": {
                    "net": "http://%s:%s@bssstash.corp-it.cc:7990/scm/cwnet/core.git" % (self._credentials.get("git")["user"], self._credentials.get("git")["pass"]),
                    "bus": "http://%s:%s@bssstash.corp-it.cc:7990/scm/cwcbus/core.git" % (self._credentials.get("git")["user"], self._credentials.get("git")["pass"]),
                }
            }
            if bam:
                bamboo = Bamboo(
                    url=self._credentials.get("atlassian")["url"],
                    username=self._credentials.get("atlassian")["user"],
                    password=self._credentials.get("atlassian")["pass"],
                    advanced_mode=True
                )
                if bam == "panama":
                    if action == 'build':
                        plan = bamboo.get_plan('CMS-SITCWPNEG')
                        the_build = bamboo.execute_build(
                            plan_key=plan.json().get('key'))
                        click.echo(click.style('Build execution status: {}'.format(
                            the_build.status_code), fg='green'))
                        if the_build.status_code == 200:
                            click.echo(click.style("Build key: {}".format(
                                the_build.json().get("buildResultKey")), fg='green'))
                            click.echo(
                                click.style(the_build.json().get("link", {}).get('href'), fg='green'))
                        else:
                            click.echo(click.style("Execution failed!", fg='red'))
                            click.echo(click.style(
                                the_build.json().get("message"), fg='red'))
                    elif action == 'deploy':
                        res = requests.get(
                            'https://bamboo-qa.cwc-apps.com/rest/api/latest/deploy/project/all', auth=(self._credentials.get("atlassian")["user"], self._credentials.get("atlassian")["pass"]))
                        resDep = requests.get(
                            'https://bamboo-qa.cwc-apps.com/rest/api/latest/deploy/project/9797640/versions', auth=(self._credentials.get("atlassian")["user"], self._credentials.get("atlassian")["pass"]))
                        releaseName = 'release-{}'.format(int(resDep.json()['versions'][0]['name'].replace('release-', '')) + 1)
                        planResultNum = resDep.json()['versions'][0]['items'][0]['planResultKey']['resultNumber']+1
                        planResultKey = '{}-{}'.format(resDep.json()['versions'][0]['items'][0]['planResultKey']['entityKey']['key'], planResultNum)
                        job = requests.post('https://bamboo-qa.cwc-apps.com/rest/api/latest/deploy/project/9797640/version',
                                            auth=(self._credentials.get("atlassian")["user"], self._credentials.get("atlassian")["pass"]),
                                            json={"planResultKey": planResultKey, "name": releaseName},
                                            headers={"Content-Type": "application/json", "Accepts": "application/json"})
                        for item in res.json():
                            if 'planKey' in item:
                                # Name: CW Panama Negocios - QAT key: 9797635
                                # Name: CW Panama Negocios - STG key: 9797638
                                # Name: CW Panama Negocios - PRD key: 9797640
                                # IN THIS CASE I WANT TO USE PROD
                                if item['planKey']['key'] == 'CMS-SITCWPNEG' and item['key']['key'] == '9797640':
                                    for env in item['environments']:
                                        releaseJob = requests.post(
                                            'https://bamboo-qa.cwc-apps.com/rest/api/latest/queue/deployment/?environmentId={}&versionId={}'.format(env['id'], job.json()['id']),
                                            auth=(self._credentials.get("atlassian")["user"], self._credentials.get("atlassian")["pass"]),
                                            headers={"Accepts": "application/json"})
                                        print(releaseJob.text)
                                        click.echo(click.style("ENVIRONMENT RELEASED: {}".format(env['name']), fg='green'))
            if clone:
                click.echo(click.style('Cloning %s' % (clone), fg='green'))
                if clone == "panama":
                    url = self._repos.get("flow")[clone]
                    path = "%s/sites/negocios.masmovilpanama.com" % (
                        self._cloneDirs.get("flow"))
                    click.echo(click.style('clone url %s' % (url), fg='green'))
                    self.gitClone(url, path)
                elif clone == "main":
                    url = self._repos.get("flow")[clone]
                    path = "%s" % (self._cloneDirs.get("flow"))
                    click.echo(click.style('clone url %s' % (url), fg='green'))
                    self.gitClone(url, path)
                elif clone == "bb":
                    url = self._repos.get("flow")[clone]
                    path = "%s/sites/flowbusiness.co.barbados" % (
                        self._cloneDirs.get("flow"))
                    click.echo(click.style('clone url %s' % (url), fg='green'))
                    self.gitClone(url, path)
                elif clone == "trinidad":
                    url = self._repos.get("flow")[clone]
                    path = "%s/sites/flowbusiness.co.trinidad-and-tobago" % (
                        self._cloneDirs.get("flow"))
                    click.echo(click.style('clone url %s' % (url), fg='green'))
                    self.gitClone(url, path)
                elif clone == "jamaica":
                    url = self._repos.get("flow")[clone]
                    path = "%s/sites/flowbusiness.co.jamaica" % (
                        self._cloneDirs.get("flow"))
                    click.echo(click.style('clone url %s' % (url), fg='green'))
                    self.gitClone(url, path)
                elif clone == "net":
                    url = self._repos.get("cw")[clone]
                    path = "%s" % (self._cloneDirs.get("cwnet"))
                    click.echo(click.style('clone url %s' % (url), fg='green'))
                    self.gitClone(url, path)
                elif clone == "bus":
                    url = self._repos.get("cw")[clone]
                    path = "%s" % (self._cloneDirs.get("flow"))
                    click.echo(click.style('clone url %s' % (url), fg='green'))
                    self.gitClone(url, path)
                elif clone == "flow":
                    url = self._repos.get("flow")[clone]
                    path = "%s" % (self._cloneDirs.get("flowb"))
                    click.echo(click.style('clone url %s' % (url), fg='green'))
                    self.gitClone(url, path)
            if dock:
                if dock == "php":
                    subprocess.run(
                        ["docker-compose", "-f", "../liberty_docker/php/docker-compose.yaml", "up", "-d", "--build"])
                    click.echo(click.style('Done Docker', fg='green'))
                elif dock == "mysql":
                    subprocess.run(
                        ["docker-compose", "-f", "../liberty_docker/mysql/docker-compose.yaml", "up", "-d", "--build"])
                    click.echo(click.style('Done Docker', fg='green'))
                elif dock == "apache":
                    subprocess.run(
                        ["docker-compose", "-f", "../liberty_docker/apache/docker-compose.yaml", "up", "-d", "--build"])
                    click.echo(click.style('Done Docker', fg='green'))
                elif dock == "composer":
                    subprocess.run(["docker-compose", "-f", "../liberty_docker/php/docker-compose.yaml",
                                    "run", "--rm", "cw-php", "composer", "install"])
                    click.echo(click.style('Done Docker', fg='green'))
            if sqlimport:
                if sqlimport == "panama":
                    self.sqlImport("c_", "negocios_masmovilpanama_com")
                if sqlimport == "flow":
                    self.sqlImport("f_", "flowbusiness_co")
                elif sqlimport == "trinidad":
                    self.sqlImport("e_", "flowbusiness_tt")
                elif sqlimport == "bus":
                    self.sqlImport("d_", "cwcbusin_wp.sql")
            if sqlexport:
                if sqlexport == "panama":
                    self.sqlExport("c_", "negocios_masmovilpanama_com")
                elif sqlexport == "bus":
                    self.sqlExport("d_", "cwcbusin_wp")
                elif sqlexport == "trinidad":
                    self.sqlExport("e_", "flowbusiness_tt")
                elif sqlexport == "bb":
                    self.sqlExport("b_", "flowbusiness_bb")
                elif sqlexport == "jamaica":
                    self.sqlExport("h_", "flowbusiness_jm")
            if media:
                if media == "panama":
                    if path is None:
                        path = "files"
                    print('path')
                    print(path)
                    self.downloadDir(
                        "/var/www/html/flowbusiness.co/sites/negocios.masmovilpanama.com",
                        os.path.join(self._cloneDirs.get("flow"), "sites", "negocios.masmovilpanama.com"),
                        "10.255.229.14",
                        path
                    )
                elif media == "trinidad":
                    if path is None:
                        path = "files"
                    print("ptah", path)
                    print(os.path.join(self._cloneDirs.get(
                        "flow"), "sites", "flowbusiness.co.trinidad-and-tobago"))
                    self.downloadDir(
                        "/var/www/html/flowbusiness.co/sites/flowbusiness.co.trinidad-and-tobago",
                        os.path.join(self._cloneDirs.get("flow"), "sites", "flowbusiness.co.trinidad-and-tobago"), "10.255.229.14",
                        path
                    )
                elif media == "jamaica":
                    if path is None:
                        path = "files"
                    print("ptah", path)
                    print(os.path.join(self._cloneDirs.get(
                        "flow"), "sites", "flowbusiness.co.jamaica"))
                    self.downloadDir(
                        "/var/www/html/flowbusiness.co/sites/flowbusiness.co.jamaica",
                        os.path.join(self._cloneDirs.get("flow"), "sites", "flowbusiness.co.jamaica"), "10.255.229.14",
                        path
                    )
                elif media == "bus":
                    if path is None:
                        path = "uploads"
                    print(path)
                    self.downloadDir(
                        "/var/www/html/cwcbusiness/wp-content",
                        os.path.join(self._cloneDirs.get("bus"), "wp-content"),
                        "10.255.229.17",
                        path
                    )
            if rok:
                if rok != None:
                    ngrok.set_auth_token(self._credentials.get("rok")["api"])
                    http_tunnel = ngrok.connect()
                    ngrok_process = ngrok.get_ngrok_process()
                    try:
                        # Block until CTRL-C or some other terminating event
                        click.echo(click.style('Summoning server !', fg='yellow'))
                        tunnels = ngrok.get_tunnels()
                        with open(r'./drupal-source/sites.yml', encoding="utf-8") as file:
                            data = yaml.load(file, Loader=yaml.FullLoader)
                        f = open("./flow-business/sites/sites.php", "w")
                        f.write("<?php\n")
                        f.write("$sites = array(\n")
                        for key in data["sites"]:
                            f.write("'{}' => '{}',\n".format(key, data["sites"][key]))
                        route = None
                        if rok == "panama":
                            route = "negocios.masmovilpanama.com"
                        elif rok == "trinidad":
                            route = "flowbusiness.co.trinidad-and-tobago"
                        elif rok == "jamaica":
                            route = "flowbusiness.co.jamaica"
                        elif rok == "barbados":
                            route = "flowbusiness.co.barbados"
                        if route != None:
                            f.write("'{}' => '{}',\n".format(tunnels[0].public_url.replace("https://", ""), route))
                        f.write(");\n")
                        f.close()
                        click.echo(click.style('Ready to rock !', blink=True, fg='green'))
                        click.echo(click.style('Live on: {}'.format(tunnels[0].public_url), fg='green'))
                        ngrok_process.proc.wait()
                    except KeyboardInterrupt:
                        click.echo(click.style('Server KILLED !', fg='red'))
                        ngrok.kill()
            if copy:
                flowDir = self._cloneDirs.get("flowb")
                if copy == "sites":
                    with open(r'./drupal-source/sites.yml', encoding="utf-8") as file:
                        data = yaml.load(file, Loader=yaml.FullLoader)
                    f = open("./flow-business/web/sites/sites.php", "w")
                    f.write("<?php\n")
                    f.write("$sites = array(\n")
                    for key in data["sites"]:
                        f.write("'{}' => '{}',\n".format(key, data["sites"][key]))
                    f.write(");\n")
                    f.close()
                elif copy == "panama":
                    # shutil.copy("./drupal-source/%s/settings.php" % (copy), os.path.join(flowDir, "web", "sites", "negocios.masmovilpanama.com", "settings.php"))
                    shutil.copy("./drupal-source/services.yml", os.path.join(flowDir, "web", "sites", "negocios.masmovilpanama.com", "services.yml"))
                elif copy == "trinidad":
                    # shutil.copy("./drupal-source/%s/settings.php" % (copy), os.path.join(flowDir, "web", "sites", "flowbusiness.co.trinidad-and-tobago", "settings.php"))
                    shutil.copy("./drupal-source/services.yml", os.path.join(flowDir, "web", "sites", "flowbusiness.co.trinidad-and-tobago", "services.yml"))
                elif copy == "jamaica":
                    # shutil.copy("./drupal-source/%s/settings.php" % (copy), os.path.join(flowDir, "sites", "flowbusiness.co.jamaica", "settings.php"))
                    shutil.copy("./drupal-source/services.yml", os.path.join(flowDir, "web", "sites", "flowbusiness.co.jamaica", "services.yml"))
                elif copy == "barbados":
                    # shutil.copy("./drupal-source/%s/settings.php" % (copy), os.path.join(flowDir, "web", "sites", "flowbusiness.co.barbados", "settings.php"))
                    shutil.copy("./drupal-source/services.yml", os.path.join(flowDir, "web", "sites", "flowbusiness.co.barbados", "services.yml"))
                elif copy == "bus":
                    shutil.copy("./wp-source/business/.htaccess",
                                os.path.join(self._cloneDirs.get("bus"), ".htaccess"))
                    shutil.copy("./wp-source/business/wp-config.php",
                                os.path.join(self._cloneDirs.get("bus"), "wp-config.php"))
                elif copy == "net":
                    shutil.copy("./wp-source/net/.htaccess",
                                os.path.join(self._cloneDirs.get("cwnet"), ".htaccess"))
                    shutil.copy("./wp-source/net/wp-config.php",
                                os.path.join(self._cloneDirs.get("cwnet"), "wp-config.php"))
            if flush:
                print('flush')
                if flush == "panama":
                    # docker-compose -f ../liberty_docker/php/docker-compose.yaml run --rm  cw-php vendor/bin/drush --uri=flowpanama.com  cache-rebuild -vvv
                    subprocess.run(["docker-compose", "-f", "../liberty_docker/php/docker-compose.yaml", "run",
                                    "--rm", "cw-php", "vendor/bin/drush", "--uri=flowpanama.com", "cache-rebuild", "-vvv"])
                    click.echo(click.style('Done Flush in panama', fg='green'))
                elif flush == "trinidad":
                    subprocess.run(["docker-compose", "-f", "../liberty_docker/php/docker-compose.yaml", "run", "--rm",
                                    "cw-php", "vendor/bin/drush", "--uri=flowbusiness.co.trinidad-and-tobago", "cache-rebuild", "-vvv"])
                    click.echo(click.style('Done Flush in panama', fg='green'))
                elif flush == "barbados":
                    subprocess.run(["docker-compose", "-f", "../liberty_docker/php/docker-compose.yaml", "run", "--rm",
                                    "cw-php", "vendor/bin/drush", "--uri=flowbusiness.co.barbados", "cache-rebuild", "-vvv"])
                    click.echo(click.style('Done Flush in panama', fg='green'))
                elif flush == "jamaica":
                    subprocess.run(["docker-compose", "-f", "../liberty_docker/php/docker-compose.yaml", "run", "--rm",
                                    "cw-php", "vendor/bin/drush", "--uri=flowbusiness.co.jamaica", "cache-rebuild", "-vvv"])
                    click.echo(click.style('Done Flush in panama', fg='green'))
                elif flush == "install":
                    subprocess.run(["docker-compose", "-f", "../liberty_docker/php/docker-compose.yaml",
                                    "run", "--rm", "cw-php", "composer require drush/drush"])
                    click.echo(click.style('Done Flush in panama', fg='green'))
        else:
            click.echo(click.style(
                'Environment variables not found. Check your .env file', fg='red'))

    def gitClone(self, cloneUrl, clonePath):
        if not os.path.exists(clonePath):
            os.makedirs(clonePath)
        else:
            shutil.rmtree(clonePath)
        git.Repo.clone_from(cloneUrl, clonePath, progress=Progress())
        click.echo(click.style('Done cloning !', fg='green'))

    def sqlImport(self, prefix, db):
        with open(f"../liberty_docker/mysql/dump/{prefix}{db}.sql") as input_file:
            subprocess.run(["docker", "exec", "-i", "cw-mysql", "/usr/bin/mysql", "-u", "root", "--password=root", "{db}".format(db=db)], stdin=input_file, capture_output=True)
        click.echo(click.style('Done Importing', fg='green'))

    def sqlExport(self, prefix, db):
        sql = subprocess.run(["docker", "exec", "-i", "cw-mysql", "mysqldump", "-uroot",
                              "-proot", "--databases", "{db}".format(db=db)], stdout=subprocess.PIPE)
        sys.stdout = open(
            "../liberty_docker/mysql/dump/{prefix}{db}.sql".format(prefix=prefix, db=db), 'wb')
        sys.stdout.write(sql.stdout)
        sys.stdout.close()
        # click.echo(click.style('Done Exporting', fg='green'))

    def printProgressDecimal(self, x, y):
        if int(100*(int(x)/int(y))) % self._progressEveryPercent == 0 and self._progressDict[str(int(100*(int(x)/int(y))))] == "":
            click.echo(click.style("{}% ({} Transfered(B)/ {} Total File Size(B))".format(
                str("%.2f" % (100*(int(x)/int(y)))), x, y), fg='blue'))
            self._progressDict[str(int(100*(int(x)/int(y))))] = "1"

    # todo: change walk to gz zip compress the folder and then uncompress it (more faster)
    def sftp_walk(self, remotepath, sftp, static_path, local_path):
        abspath = remotepath.replace(static_path, local_path)
        path = remotepath
        for f in sftp.listdir_attr(remotepath):
            if S_ISDIR(f.st_mode):
                if not os.path.exists(os.path.join(abspath, f.filename)):
                    os.makedirs(os.path.join(abspath, f.filename))
                self.sftp_walk(os.path.join(remotepath, f.filename),
                               sftp, static_path, local_path)
            else:
                if not os.path.exists(os.path.join(abspath, f.filename)):
                    click.echo(click.style("Found file -> " +
                                           os.path.join(abspath, f.filename), fg='yellow'))
                    sftp.get(os.path.join(os.path.join(path, f.filename)), localpath=os.path.join(
                        abspath, f.filename), callback=lambda x, y: self.printProgressDecimal(x, y))
                    click.echo(click.style("100% - Downloaded !", fg='blue'))

    def downloadDir(self, remote, local, host, files):
        paramiko.util.log_to_file('/tmp/paramiko.log')
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, port=22, username=self._credentials.get(
            "ssh")["user"], password=self._credentials.get("ssh")["pass"])
        sftp = ssh.open_sftp()
        ssh.get_transport().window_size = 3 * 1024 * 1024
        members = None
        cmd = 'cd {remote} && tar cf - "{files}" --exclude="ShortpixelBackups" --exclude="cache" --exclude="elementor" --exclude="file-manager" --exclude="flags" --exclude="pum" --exclude="css" --exclude="js" --exclude="php" --strip-components=5 2>/dev/null | gzip -1c 2>/dev/null'.format(
            remote=remote, files=files)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdin.close()
        # <TRICK
        # print(os.path.expanduser("~/Documents/dev/dock-roboto/{local}".format(local=local)))
        sys.stdout = open("{local}/temp.tar.gz".format(local=local), 'wb')
        sys.stdout.write(stdout.read())
        sys.stdout.close()

        """
        Extracts `tar_file` and puts the `members` to `path`.
        If members is None, all members on `tar_file` will be extracted.
        """
        tar = tarfile.open(
            "{local}/temp.tar.gz".format(local=local), mode="r:gz")
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


@ click.group(invoke_without_command=True)
@ click.option('-c', '--clone', "clone", type=str)
@ click.option('-d', '--dock', "dock", type=str)
@ click.option('-m', '--media', "media", type=str)
@ click.option('-p', '--path', "path", type=str)
@ click.option('-p', '--action', "action", type=str)
@ click.option('-sqli', '--sqlimport', "sqlimport", type=str)
@ click.option('-cp', '--copy', "copy", type=str)
@ click.option('-sqle', '--sqlexport', "sqlexport", type=str)
@ click.option('-f', '--flush', "flush", type=str)
@ click.option('-b', '--bam', "bam", type=str)
@ click.option('-r', '--rok', "rok", type=str)
@ click.pass_context
def cli(ctx, clone, dock, media, sqlimport, copy, sqlexport, flush, path, bam, action, rok):
    ctx.obj = Roboto(
        clone=clone,
        dock=dock,
        media=media,
        copy=copy,
        sqlexport=sqlexport,
        flush=flush,
        sqlimport=sqlimport,
        path=path,
        bam=bam,
        action=action,
        rok=rok
    )
