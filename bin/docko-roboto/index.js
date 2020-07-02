#!/usr/bin/env node
const git = require("nodegit");
const SSH = require("ssh2");
const tar = require("tar-fs");
const zlib = require("zlib");
const { exec } = require("child_process");
const fs = require("fs-extra");
const { URL } = require("url");
const argv = require("yargs").argv;
require("custom-env").env();

class DockoRoboto {
  constructor() {
    console.log("NODE INIT");
    //NODE 8 IMPLEMENTATION
    this.USER = process.env.GIT_USER;
    this.PASS = process.env.GIT_PASS;
    this.USER_SSH = process.env.SSH_USER;
    this.PASS_SSH = process.env.SSH_PASS;
    this.REPO_URL =
      "http://" +
      this.USER +
      ":" +
      this.PASS +
      "@bssstash.corp-it.cc:7990/scm/fb/flowbusiness_co.git";
    this.REPO_BARBADOS =
      "http://" +
      this.USER +
      ":" +
      this.PASS +
      "@bssstash.corp-it.cc:7990/scm/fb/sites_flowbusiness_bb.git";
    this.REPO_PANAMA =
      "http://" +
      this.USER +
      ":" +
      this.PASS +
      "@bssstash.corp-it.cc:7990/scm/fb/sites_masmovilpanama_negocios.git";
    this.CLONE_DIR = "./flowbusiness_co";
    if (argv._.includes("clone")) {
      this.cloneMain();
      this.clonePanama();
      this.cloneBB();
    }

    switch (argv.dock) {
      case "all":
        this.doDocker();
        break;
      case "php":
        this.doPHP();
        break;
      case "mysql":
        this.doMysql();
        break;
      case "composer":
        this.doComposer();
        break;
    }

    switch (argv.copy) {
      case "all":
        this.copyPanamaSettings(
          this.CLONE_DIR + "/sites/negocios.masmovilpanama.com/"
        );
        this.copyBBSettings(
          this.CLONE_DIR + "/sites/flowbusiness.co.barbados/"
        );
        this.copySitesSettings(this.CLONE_DIR + "/sites/");
        break;
      case "panama":
        this.copyPanamaSettings(
          this.CLONE_DIR + "/sites/negocios.masmovilpanama.com/"
        );
        break;
      case "bb":
        this.copyBBSettings(
          this.CLONE_DIR + "/sites/flowbusiness.co.barbados/"
        );
        break;
      case "sites":
        this.copySitesSettings(this.CLONE_DIR + "/sites/");
        break;
    }
  }

  cloneMain() {
    let authAttempted = false;
    console.log("CLONING MAIN");
    async () => {
      await fs.emptyDir(CLONE_DIR);
      await git.Clone.clone(REPO_URL, CLONE_DIR, {
        fetchOpts: {
          callbacks: {
            transferProgress: function (progress) {
              const percentaje =
                (100 *
                  (progress.receivedObjects() + progress.indexedObjects())) /
                (progress.totalObjects() * 2);
              console.log("CLONING %", percentaje.toFixed(2));
            },
            certificateCheck: () => 1,
            credentials: (url, username) => {
              if (authAttempted) return git.Cred.defaultNew();
              authAttempted = true;
              url = new URL(url);
              return git.Cred.userpassPlaintextNew(url.username, url.password);
            },
          },
        },
      }).then(function (repository) {
        // Work with the repository object here.
        console.log("DONE CLONING");
      });
    };
  }

  copyPanamaSettings(localDir) {
    fs.copyFile(
      "./drupal-source/panama/settings.php",
      localDir + "settings.php",
      (err) => {
        if (err) throw err;
        console.log("DOne copy settings.php");
      }
    );
    fs.copyFile(
      "./drupal-source/services.yml",
      localDir + "services.yml",
      (err) => {
        if (err) throw err;
        console.log("DOne copy servikces.yml");
      }
    );
  }

  copySitesSettings(localDir) {
    fs.copyFile("./drupal-source/sites.php", localDir + "sites.php", (err) => {
      if (err) throw err;
      console.log("DOne copy sites.php");
    });
  }

  copyBBSettings(localDir) {
    fs.copyFile(
      "./drupal-source/barbados/settings.php",
      localDir + "settings.php",
      (err) => {
        if (err) throw err;
        console.log("DOne copy settings.php");
      }
    );
    fs.copyFile(
      "./drupal-source/services.yml",
      localDir + "services.yml",
      (err) => {
        if (err) throw err;
        console.log("DOne copy servikces.yml");
      }
    );
  }

  clonePanama() {
    async () => {
      await fs.emptyDir(this.CLONE_DIR + "/sites/negocios.masmovilpanama.com");
      await git.Clone.clone(
        this.REPO_PANAMA,
        this.CLONE_DIR + "/sites/negocios.masmovilpanama.com",
        {
          fetchOpts: {
            callbacks: {
              transferProgress: function (progress) {
                const percentaje =
                  (100 *
                    (progress.receivedObjects() + progress.indexedObjects())) /
                  (progress.totalObjects() * 2);
                console.log("CLONING %", percentaje.toFixed(2));
              },
              certificateCheck: () => 1,
              credentials: (url, username) => {
                if (authAttempted) return git.Cred.defaultNew();
                authAttempted = true;
                url = new URL(url);
                return git.Cred.userpassPlaintextNew(
                  url.username,
                  url.password
                );
              },
            },
          },
        }
      ).then(function (repository) {
        const localDir = CLONE_DIR + "/sites/negocios.masmovilpanama.com/";
        // Work with the repository object here.
        copyPanamaSettings(localDir);
        if (!fs.existsSync(localDir + "files/")) {
          fs.mkdirSync(localDir + "files/");
        }
        fs.emptyDir(localDir + "files/");
        var conn = new SSH();
        var connectionSettings = {
          // The host URL
          host: "10.255.229.14",
          // The port, usually 22
          port: 22,
          // Credentials
          username: USER_SSH,
          password: PASS_SSH,
        };
        conn
          .on("ready", function () {
            // Use the transfer directory
            transferDirectory(
              // The SSH2 connection
              conn,
              // The remote folder of your unix server that you want to back up
              "/var/www/html/flowbusiness.co/sites/negocios.masmovilpanama.com/files",
              // Local path where the files should be saved
              localDir,
              // Define a compression value (true for default 6) with a numerical value
              true,
              // A callback executed once the transference finishes
              function (err) {
                if (err) {
                  throw err;
                }

                console.log("Remote directory succesfully downloaded!");

                // Finish the connection
                conn.end();
              }
            );
          })
          .connect(connectionSettings);
      });
    };
  }

  cloneBB() {
    async () => {
      console.log("CLONING BARBADOS");
      await git.Clone.clone(
        REPO_BARBADOS,
        CLONE_DIR + "/sites/flowbusiness.co.barbados",
        {
          fetchOpts: {
            callbacks: {
              transferProgress: function (progress) {
                const percentaje =
                  (100 *
                    (progress.receivedObjects() + progress.indexedObjects())) /
                  (progress.totalObjects() * 2);
                console.log("CLONING %", percentaje.toFixed(2));
              },
              certificateCheck: () => 1,
              credentials: (url, username) => {
                if (authAttempted) return git.Cred.defaultNew();
                authAttempted = true;
                url = new URL(url);
                return git.Cred.userpassPlaintextNew(
                  url.username,
                  url.password
                );
              },
            },
          },
        }
      ).then(function (repository) {
        const localDir = CLONE_DIR + "/sites/flowbusiness.co.barbados/";
        // Work with the repository object here.
        this.copyBBSettings(localDir);
        if (!fs.existsSync(localDir + "files/")) {
          fs.mkdirSync(localDir + "files/");
        }
        fs.emptyDir(localDir + "files/");
        var conn = new SSH();
        var connectionSettings = {
          // The host URL
          host: "10.255.229.14",
          // The port, usually 22
          port: 22,
          // Credentials
          username: USER_SSH,
          password: PASS_SSH,
        };
        conn
          .on("ready", function () {
            // Use the transfer directory
            transferDirectory(
              // The SSH2 connection
              conn,
              // The remote folder of your unix server that you want to back up
              "/var/www/html/flowbusiness.co/sites/flowbusiness.co.barbados/files",
              // Local path where the files should be saved
              localDir,
              // Define a compression value (true for default 6) with a numerical value
              true,
              // A callback executed once the transference finishes
              function (err) {
                if (err) {
                  throw err;
                }

                console.log("Remote directory succesfully downloaded!");

                // Finish the connection
                conn.end();
              }
            );
          })
          .connect(connectionSettings);
      });
    };
  }

  doNet() {
    console.log(`- Creating network 。.:☆*:･'(*⌒―⌒*)))`);
    exec("docker network create cw_net", (error, stdout, stderr) => {
      if (error) {
        console.log(`error: ${error.message}`);
        return;
      }
    });
  }

  doPHP() {
    console.log(`- Running PHP Container <(￣︶￣)>`);
    exec(
      "docker-compose -f ../soho_docker/php/docker-compose.yaml up -d --build",
      (error, stdout, stderr) => {
        if (error) {
          console.log(`error: ${error.message}`);
          return;
        }
      }
    );
  }

  doMysql() {
    console.log(`- Running Mysql Container (￣ω￣)`);
    exec(
      "docker-compose -f ../soho_docker/mysql/docker-compose.yaml up -d --build",
      (error, stdout, stderr) => {
        if (error) {
          console.log(`error: ${error.message}`);
          return;
        }
      }
    );
  }

  doWeb() {
    console.log(`- Running Web Container <(￣︶￣)>`);
    exec(
      "docker-compose -f ../soho_docker/apache/docker-compose.yaml up -d --build",
      (error, stdout, stderr) => {
        if (error) {
          console.log(`error: ${error.message}`);
          return;
        }
      }
    );
  }

  doComposer() {
    console.log(
      `-- Building composer libs (this take a little while you can take a coffe (o˘◡˘o) ) (－ω－) zzZ`
    );
    exec(
      "docker-compose -f ../soho_docker/php/docker-compose.yaml run --rm  cw-php php composer.phar install",
      (error, stdout, stderr) => {
        if (error) {
          console.log(`error: ${error.message}`);
          return;
        }
        console.log(
          `! ┌( ಠ_ಠ)┘ ! Nice work now you can see the project step 1 at this address: http://flowpanama.com/ ! Enjoy !`
        );
      }
    );
  }

  doDocker() {
    console.log(`☆*:.｡.o(≧▽≦)o.｡.:*☆ INIT`);
    console.log(`- - - - - - - - - - - - - - - `);
    this.doNet();
    this.doPHP();
    this.doMysql();
    this.doWeb();
    this.doComposer();
  }

  /**
   * Transfers an entire directory locally by compressing, downloading and extracting it locally.
   *
   * @param {SSH} conn A ssh connection of the ssh2 library
   * @param {String} remotePath
   * @param {String} localPath
   * @param {Integer|Boolean} compression
   * @param {Function} cb Callback executed once the transfer finishes (success or error)
   * @see http://stackoverflow.com/questions/23935283/transfer-entire-directory-using-ssh2-in-nodejs
   */
  transferDirectory(conn, remotePath, localPath, compression, cb) {
    var cmd = 'tar cf - "' + remotePath + '" --strip-components 5 2>/dev/null';
    cmd =
      "cd " +
      remotePath +
      ' && cd .. && tar cf - "files" --strip-components=5 2>/dev/null';
    if (typeof compression === "function") {
      cb = compression;
    } else if (compression === true) {
      compression = 6;
    }

    // Apply compression if desired
    if (
      typeof compression === "number" &&
      compression >= 1 &&
      compression <= 9
    ) {
      cmd += " | gzip -" + compression + "c 2>/dev/null";
    } else {
      compression = undefined;
    }
    conn.exec(cmd, function (err, stream) {
      if (err) {
        return cb(err);
      }

      var exitErr;
      console.log(tar);
      var tarStream = tar.extract(localPath);

      tarStream.on("finish", function () {
        cb(exitErr);
      });

      stream
        .on("exit", function (code, signal) {
          if (typeof code === "number" && code !== 0) {
            exitErr = new Error("Remote process exited with code " + code);
          } else if (signal) {
            exitErr = new Error("Remote process killed with signal " + signal);
          }
        })
        .stderr.resume();

      if (compression) {
        stream = stream.pipe(zlib.createGunzip());
      }

      stream.pipe(tarStream);
    });
  }
}
new DockoRoboto();
