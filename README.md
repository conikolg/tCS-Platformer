# theCoderSchool Frisco Coaches' Project (August 2022 Coder Fair)

Welcome to the repository for the platformer game developed by the coaches at theCoderSchool Frisco!

You should almost always work on your own branch and merge into `main` when ready. Make sure to push/pull frequently.

## Installation and Setup

1. Clone this repo. You can do with GitHub Desktop or via `git clone` with HTTPS or SSH.
2. Create a virtual environment to work in. If you're using PyCharm or another IDE, it may help you
    make one. But if you need the command, one way to do it is with:
    ```
    python3 -m venv venv
    ```
   
    If you get an error about an unspecified file, then try this instead:
    ```
    python3 -m pip install --upgrade virtualenv
    python3 -m virtualenv venv
    ```
   
    This will create a folder inside the project folder called `venv`. You don't need to ever
    look inside it or care about its contents - that'll be managed by `pip` and it is already
    ignored by the `.gitignore` file (don't worry about pushing it to GitHub).

    You need to make sure your virtual environment is activated. You should see `(venv)` at the
    beginning of your terminal prompt if you are. __Your IDE may activate it for you.__ When it's 
    activated, your `python` and `pip` commands are redirected to the virtual environment and
    do not affect the rest of your system.

    If you are not activated...

    ### macOS and Linux

    Activation will most likely work without issue if you run the command:
    ``` bash
    source venv/bin/activate
    ```
   
    To deactivate it, just run this command:
   ``` bash
    deactivate
    ```

    ### Windows

    First, consider upgrading your operating system. No, I don't mean Windows 11.

    Windows normally won't let you run the activation script by default. So you'll need to first
    open PowerShell and run this command (one-time only):
    ``` PowerShell
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
    ```
   
    Then activate the environment.
    
    Use this for PowerShell:
    ``` PowerShell
    .\venv\Scripts\activate.ps1
    ```
   
    Use this for Windows Command Prompt:
    ``` cmd
    .\venv\Scripts\activate.bat
    ```
   
    Either way, to deactivate it, just run this command:
    ``` PowerShell
    deactivate
    ```

3. Install all necessary Python modules. A `requirements.txt` file is provided to make this easy.

    Run the following command in your terminal:
    ```
    pip install -r requirements.txt
    ```
   
    If `pip` isn't recognized, try this instead:
    ```
    python3 -m pip install -r requirements.txt
    ```

    When you are developing this project, feel free to rely on additional third party modules, but please make sure you
    include the correct package names in `requirements.txt` as well when you do that.

    You can rerun this command anytime - it should ensure that you have all the dependencies needed to run the project.
