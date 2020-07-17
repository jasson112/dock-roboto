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
const ora = require("ora");
const spinner = ora("Docko Roboto").start();
const spawn = require("child_process").spawn;

class DockoRoboto {
  constructor() {
    spinner.color = "yellow";
    spinner.text = "NODE INIT";
    //NODE 8 IMPLEMENTATION
    this.USER = process.env.GIT_USER;
    this.PASS = process.env.GIT_PASS;
    this.USER_SSH = process.env.SSH_USER;
    this.PASS_SSH = process.env.SSH_PASS;
    this.REPOS = {
      flow: {
        main:
          "http://" +
          this.USER +
          ":" +
          this.PASS +
          "@bssstash.corp-it.cc:7990/scm/fb/flowbusiness_co.git",
        bb:
          "http://" +
          this.USER +
          ":" +
          this.PASS +
          "@bssstash.corp-it.cc:7990/scm/fb/sites_flowbusiness_bb.git",
        panama:
          "http://" +
          this.USER +
          ":" +
          this.PASS +
          "@bssstash.corp-it.cc:7990/scm/fb/sites_masmovilpanama_negocios.git",
      },
      cw: {
        net:
          "http://" +
          this.USER +
          ":" +
          this.PASS +
          "@bssstash.corp-it.cc:7990/scm/cwnet/core.git",
        business:
          "http://" +
          this.USER +
          ":" +
          this.PASS +
          "@bssstash.corp-it.cc:7990/scm/cwcbus/core.git",
      },
    };
    this.CLONE_DIR = {
      flow: "./flowbusiness_co",
      cwnet: "./cwnetworks.com",
      bus: "./cwbusiness.com",
    };

    switch (argv.clone) {
      case "all":
        this.cloneMain();
        this.clonePanama();
        this.cloneBB();
        break;
      case "main":
        this.cloneMain();
        break;
      case "panama":
        this.clonePanama();
        break;
      case "bb":
        this.cloneBB();
        break;
      case "net":
        this.cloneNetworks();
        break;
      case "bus":
        this.cloneBusiness();
        break;
    }

    switch (argv.dock) {
      case "all":
        this.doDocker();
        break;
      case "php":
        this.doPHP(function () {
          spinner.succeed("Dock running succesfully");
        });
        break;
      case "web":
        this.doWeb(function () {
          spinner.succeed("Dock running succesfully");
        });
        break;
      case "mysql":
        this.doMysql();
        break;
      case "composer":
        this.doComposer();
        break;
    }

    switch (argv.media) {
      case "bus":
        this.downloadMediaBusiness(function () {
          spinner.succeed("Download succesfully");
        });
        break;
      case "panama":
        this.downloadMediaPanama(function () {
          spinner.succeed("Download succesfully");
        });
        break;
    }

    switch (argv.copy) {
      case "all":
        this.copyPanamaSettings(
          this.CLONE_DIR.flow + "/sites/negocios.masmovilpanama.com/"
        );
        this.copyBBSettings(
          this.CLONE_DIR.flow + "/sites/flowbusiness.co.barbados/"
        );
        this.copySitesSettings(this.CLONE_DIR.flow + "/sites/");
        break;
      case "panama":
        this.copyPanamaSettings(
          this.CLONE_DIR.flow + "/sites/negocios.masmovilpanama.com/"
        );
        break;
      case "bb":
        this.copyBBSettings(
          this.CLONE_DIR.flow + "/sites/flowbusiness.co.barbados/"
        );
        break;
      case "sites":
        this.copySitesSettings(this.CLONE_DIR.flow + "/sites/");
        break;
      case "business":
        spinner.color = "yellow";
        spinner.text = "Copy busniess site settings";
        this.copyBusinessSettings(this.CLONE_DIR.bus + "/", function () {
          spinner.succeed("Bussines Copy files DONE !");
        });
        break;
    }

    switch (argv.sqlimport) {
      case "panama":
        this.doMysqlImport("negocios_masmovilpanama_com", "c_", function () {
          spinner.succeed("Import Done !");
        });
        break;
    }

    switch (argv.sqlexport) {
      case "panama":
        this.doMysqlExport("negocios_masmovilpanama_com", "c_", function () {
          spinner.succeed("Export Done !");
        });
        break;
    }
  }

  cloneMain() {
    let authAttempted = false;
    spinner.color = "blue";
    spinner.text = "CLONING MAIN";
    async () => {
      await fs.emptyDir(CLONE_DIR.flow);
      await git.Clone.clone(this.REPOS.flow.main, CLONE_DIR.flow, {
        fetchOpts: {
          callbacks: {
            transferProgress: function (progress) {
              const percentaje =
                (100 *
                  (progress.receivedObjects() + progress.indexedObjects())) /
                (progress.totalObjects() * 2);
              spinner.color = "green";
              spinner.text = "CLONING %" + percentaje.toFixed(2);
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
        spinner.prefixText = "DONE CLONING";
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

  copyBusinessSettings(localDir, callback) {
    fs.copyFile(
      "./wp-source/business/wp-config.php",
      localDir + "wp-config.php",
      (err) => {
        if (err) {
          spinner.fail(err.message);
          return;
        }
        spinner.info("DOne copy wp-config.php");
        callback();
      }
    );
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

  cloneNetworks() {
    const my_this = this;
    (async () => {
      console.log("CLONING CW NETWORKS");
      await fs.emptyDir(this.CLONE_DIR.cwnet);
      await git.Clone.clone(this.REPOS.cw.net, this.CLONE_DIR.cwnet, {
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
      }).then(function (repository) {});
    })();
  }

  downloadMediaPanama(callback) {
    const my_this = this;
    const my_callback = callback;
    spinner.text = "Download bussines media";
    const localDir =
      my_this.CLONE_DIR.flow + "/sites/negocios.masmovilpanama.com/";
    // Work with the repository object here.
    my_this.copyPanamaSettings(localDir);
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
      username: my_this.USER_SSH,
      password: my_this.PASS_SSH,
    };
    conn
      .on("ready", function () {
        // Use the transfer directory
        my_this.transferDirectory(
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

            spinner.info("Remote directory succesfully downloaded!");

            // Finish the connection
            conn.end();
            my_callback();
          },
          "files"
        );
      })
      .connect(connectionSettings);
  }

  downloadMediaBusiness(callback) {
    const my_this = this;
    const my_callback = callback;
    spinner.text = "Download bussines media";
    const localDir = this.CLONE_DIR.bus + "/wp-content/";
    // Work with the repository object here.
    this.copyBBSettings(localDir);
    if (!fs.existsSync(localDir + "uploads/")) {
      fs.mkdirSync(localDir + "uploads/");
    }
    fs.emptyDir(localDir + "uploads/");
    var conn = new SSH();
    var connectionSettings = {
      // The host URL
      host: "10.255.229.17",
      // The port, usually 22
      port: 22,
      // Credentials
      username: this.USER_SSH,
      password: this.PASS_SSH,
    };
    conn
      .on("ready", function () {
        // Use the transfer directory
        my_this.transferDirectory(
          // The SSH2 connection
          conn,
          // The remote folder of your unix server that you want to back up
          "/var/www/html/cwcbusiness/wp-content/uploads",
          // Local path where the files should be saved
          localDir,
          // Define a compression value (true for default 6) with a numerical value
          true,
          // A callback executed once the transference finishes
          function (err) {
            if (err) {
              throw err;
            }
            spinner.info("Remote directory succesfully downloaded!");
            // Finish the connection
            conn.end();
            my_callback();
          },
          "uploads"
        );
      })
      .connect(connectionSettings);
  }

  cloneBusiness() {
    const my_this = this;
    (async () => {
      console.log("CLONING CW BUSINESS");
      await fs.emptyDir(this.CLONE_DIR.bus);
      await git.Clone.clone(this.REPOS.cw.business, this.CLONE_DIR.bus, {
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
      }).then(function (repository) {});
    })();
  }

  clonePanama() {
    const my_this = this;
    (async () => {
      console.log("CLONING PANAMA THEME");
      await fs.emptyDir(
        this.CLONE_DIR.flow + "/sites/negocios.masmovilpanama.com"
      );
      await git.Clone.clone(
        this.REPOS.flow.panama,
        this.CLONE_DIR.flow + "/sites/negocios.masmovilpanama.com",
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
      ).then(function (repository) {});
    })();
  }

  cloneBB() {
    const my_this = this;
    async () => {
      console.log("CLONING BARBADOS");
      await git.Clone.clone(
        this.REPOS.flow.bb,
        this.CLONE_DIR.flow + "/sites/flowbusiness.co.barbados",
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
        const localDir =
          my_this.CLONE_DIR.flow + "/sites/flowbusiness.co.barbados/";
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
          username: my_this.USER_SSH,
          password: my_this.PASS_SSH,
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
              },
              "files"
            );
          })
          .connect(connectionSettings);
      });
    };
  }

  doNet() {
    spinner.info(`- Creating network 。.:☆*:･'(*⌒―⌒*)))`);
    exec("docker network create cw_net", (error, stdout, stderr) => {
      if (error) {
        console.log(`error: ${error.message}`);
        return;
      }
      callback();
    });
  }

  doPHP(callback) {
    spinner.text = `- Running PHP Container <(￣︶￣)>`;
    exec(
      "docker-compose -f ../soho_docker/php/docker-compose.yaml up -d --build",
      (error, stdout, stderr) => {
        if (error) {
          spinner.fail(`error: ${error.message}`);
          return;
        }
        callback();
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

  doMysqlExport(db, prefix, callback) {
    spinner.info(`- Running export in Mysql Container (￣ω￣)`);
    //IMPORT
    //cat backup.sql | docker exec -i CONTAINER /usr/bin/mysql -u root --password=root DATABASE
    exec(
      "docker exec -i cw-mysql mysqldump -uroot -proot --databases " +
        db +
        " > ../soho_docker/mysql/dump/" +
        prefix +
        db +
        ".sql",
      (error, stdout, stderr) => {
        if (error) {
          spinner.fail(`error: ${error.message}`);
          return;
        }
        callback();
      }
    );
  }

  doMysqlImport(db, prefix, callback) {
    spinner.info(`- Running import in Mysql Container (￣ω￣)`);
    //IMPORT
    //cat backup.sql | docker exec -i CONTAINER /usr/bin/mysql -u root --password=root DATABASE
    exec(
      "cat ../soho_docker/mysql/dump/" +
        prefix +
        db +
        ".sql | docker exec -i cw-mysql /usr/bin/mysql -u root --password=root " +
        db,
      (error, stdout, stderr) => {
        if (error) {
          spinner.fail(`error: ${error.message}`);
          return;
        }
        callback();
      }
    );
  }

  doWeb(callback) {
    spinner.info(`- Running Web Container <(￣︶￣)>`);
    exec(
      "docker-compose -f ../soho_docker/apache/docker-compose.yaml up -d --build",
      (error, stdout, stderr) => {
        if (error) {
          spinner.fail(`error: ${error.message}`);
          return;
        }
        callback();
      }
    );
  }

  doComposer() {
    console.log(
      `-- Building composer libs (this take a little while you can take a coffe (o˘◡˘o) ) (－ω－) zzZ`
    );
    exec(
      //flowbusiness_co/sites/negocios.masmovilpanama.com/themes/custom/masmovil
      //docker-compose -f ../soho_docker/php/docker-compose.yaml run --rm  cw-php php composer.phar install -d sites/negocios.masmovilpanama.com/themes/custom/masmovil/pattern-lab
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
  transferDirectory(conn, remotePath, localPath, compression, cb, folder) {
    var cmd = 'tar cf - "' + remotePath + '" --strip-components 5 2>/dev/null';
    cmd =
      "cd " +
      remotePath +
      ' && cd .. && tar cf - "' +
      folder +
      '" --strip-components=5 2>/dev/null';
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
