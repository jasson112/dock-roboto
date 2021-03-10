# dock-roboto

# REQUIREMENtS

- Nvm with node 8. See: https://github.com/nvm-sh/nvm#installing-and-updating
- Yarn
- Docker desktop with sared drive in location on the this repo is cloned

# ROBOT COMMANDS

roboto --clone=main

# USAGE PY

1. creating virtual environment

   ```
   python3 -m venv venv/
   ```

2. activating virtual environment

   ```
   source venv/bin/activate
   ```

3. install dependencies

   ```
   pip install -r ./roboto/requirements.txt
   ```

4. isntall the command

   ```
   pip install --editable ./roboto
   ```

# USAGE

run these commands to enjoy the magic:

1. inatall dependencies

   ```
   yarn
   ```

2. initialize repos

   ```
   yarn run init
   ```

3. run sass compiler

   - in case of panama

   ```
    yarn run pattern-panama
   ```

- otherwise

  ```
   yarn run pattern-bb
  ```

4. .evn file example:

````
GIT_USER=""
GIT_PASS=""
SSH_USER=""
SSH_PASS=""
```
````
