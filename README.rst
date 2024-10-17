Here’s an updated **README** that reflects the changes we made to make `exitwp` compatible with Python 3. It also includes the necessary dependencies and installation instructions.
---

# Exitwp - WordPress to Jekyll Migration Tool

**Exitwp** is a tool for making migration from one or more WordPress blogs to the Jekyll blog engine as easy as possible.

By default, it will try to convert as much information as possible from WordPress but can also be configured to filter the amount of data it converts.



---

## Getting Started

1. Download or clone the repository:
   ```bash
   git clone https://github.com/thomasf/exitwp.git
   ```

2. Export one or more WordPress blogs using the WordPress exporter under **Tools > Export** in the WordPress admin.

3. Place all WordPress XML export files in the `wordpress-xml` directory.

4. Special note for WordPress 3.1 users: You may need to add a missing namespace in the `<rss>` tag:
   ```xml
   xmlns:atom="http://www.w3.org/2005/Atom"
   ```

5. Run `xmllint` on your export file to fix any errors, if necessary.

6. Run the converter by typing:
   ```bash
   python exitwp.py
   ```
   from the directory of the unzipped archive.

7. You should now have all the blogs converted into separate directories under the `build` directory.

---

## Runtime Dependencies

- **Python**: Now fully compatible with Python 3.  
- **html2text**: Converts HTML to markdown (Python).
- **PyYAML**: For reading configuration files and writing YAML headers (Python).
- **Beautiful Soup**: Parsing and downloading of post images/attachments (Python).

### Installing Dependencies (Ubuntu/Debian)

You can install the necessary dependencies by running the following commands:
```bash
sudo apt-get install python3-pip python3-yaml python3-bs4 python3-html2text
```

### Installing Python Dependencies Using `pip`

From the checked-out root of this project, type:
```bash
sudo pip3 install --upgrade -r pip_requirements.txt
```

Note: PyYAML may require additional packages to compile correctly under Ubuntu/Debian. You can install them with:
```bash
sudo apt-get install libyaml-dev python3-dev build-essential
```

---

## Using Vagrant for Dependency Management

If your local system is incompatible with the listed dependencies, or you'd prefer not to install them, you can use the included **Vagrantfile** to start a VM with all necessary dependencies installed.

1. Place all WordPress XML export files in the `wordpress-xml` directory.

2. In the directory of the unzipped archive, run:
   ```bash
   vagrant up
   ```

3. SSH into your Vagrant VM using:
   ```bash
   vagrant ssh
   ```

4. Navigate to the VM's shared folder:
   ```bash
   cd /vagrant
   ```

5. Run the converter by typing:
   ```bash
   python3 exitwp.py
   ```

6. After the converter completes, exit the SSH session using `exit`.

7. You should now have all the blogs converted into separate directories under the `build` directory.

8. **Important**: Once you're satisfied with the results, run `vagrant destroy -f` to shut down the VM and remove the virtual drive from your local machine.

---

## Configuration/Customization

See the `config.yaml` file for all configurable options.

Some things, like custom handling of non-standard post types, are not fully configurable through the config file. You might have to modify the source code to add custom parsing behavior.

---

## Known Issues

- Some target file names might be less than optimal.
- Rewriting of image/attachment links when they are downloaded would be a useful feature to add.
- There may be issues when migrating non-UTF-8 encoded WordPress export files (if they exist).
- Unknown item types such as `wp_template`, `feedback`, etc., are ignored as they do not map directly to Jekyll.

---

## Other Tools

A Gist to convert WP-Footnotes style footnotes to PHP Markdown Extra style footnotes:  
https://gist.github.com/1246047

---

## Credits

This project was originally created by **@thomasf** and contributors.

**Special thanks to [ChatGPT](https://chat.openai.com)** for assisting in porting the script to Python 3 and fixing compatibility issues.

---

## About

Exitwp is a tool primarily aimed at making the migration from one or more WordPress blogs to the Jekyll blog engine as easy as possible.

---

## Resources

- **Repository**: https://github.com/thomasf/exitwp
- **License**: MIT License

---

OLD ReadMe fpr Python 2.0
Feel free to modify this README if you need to add anything specific about your version or contributions.

Once you're ready, you can commit and push the README file to your GitHub repository. Let me know if you need further assistance!######
Exitwp
######

Exitwp is tool for making migration from one or more wordpress blogs to the `jekyll blog engine <https://github.com/mojombo/jekyll/>`_ as easy as possible.

By default it will try to convert as much information as possible from wordpress but can also be told to filter the amount of data it converts.

The latest version of these docs should always be available at https://github.com/thomasf/exitwp

Getting started
===============
 * `Download <https://github.com/thomasf/exitwp/zipball/master>`_ or clone using ``git clone https://github.com/thomasf/exitwp.git``
 * Export one or more wordpress blogs using the wordpress exporter under tools/export in wordpress admin.
 * Put all wordpress xml files in the ``wordpress-xml`` directory
 * Special note for Wordpress 3.1, you need to add a missing namespace in rss tag : ``xmlns:atom="http://www.w3.org/2005/Atom"``
 * Run xmllint on your export file and fix errors if there are.
 * Run the converter by typing ``python exitwp.py`` in the console from the directory of the unzipped archive
 * You should now have all the blogs converted into separate directories under the ``build`` directory

Runtime dependencies
====================
 * `Python <http://python.org/>`_ 2.6, 2.7, ???
 * `html2text <http://www.aaronsw.com/2002/html2text/>`_ :  converts HTML to markdown (python)
 * `PyYAML <http://pyyaml.org/wiki/PyYAML>`_ : Reading configuration files and writing YAML headers (python)
 * `Beautiful soup <http://www.crummy.com/software/BeautifulSoup/>`_ : Parsing and downloading of post images/attachments (python)


Installing dependencies in ubuntu/debian
----------------------------------------

   ``sudo apt-get install python-yaml python-bs4 python-html2text``

Installing Python dependencies using python package installer (pip)
-------------------------------------------------------------------

From the checked out root for this project, type:

   ``sudo pip install --upgrade  -r pip_requirements.txt``

Note that PyYAML will require other packages to compile correctly under ubuntu/debian, these are installed by typing:

   ``sudo apt-get install libyaml-dev python-dev build-essential``

Using Vagrant for dependency management
---------------------------------------

In the event your local system is incompatible with the dependencies listed (or you'd rather not install them), you can use the included Vagrantfile to start a VM with all necessary dependencies installed.

1. Lint and place all wordpress xml files in the ``wordpress-xml`` directory as mentioned above
2. In the directory of the unzipped archive, run ``vagrant up``.
3. SSH to your Vagrant VM using ``vagrant ssh``
4. Run ``cd /vagrant`` to open the VM's shared folder
5. Run the converter from the VM by typing ``python exitwp.py``
6. After the converter completes, exit the SSH session using ``exit``
7. You should now have all the blogs converted into separate directories under the ``build`` directory
8. **Important:** Once satisfied with the results, run ``vagrant destroy -f`` to shut down the VM and remove the virtual drive from your local machine

Configuration/Customization
===========================

See the `configuration file <https://github.com/thomasf/exitwp/blob/master/config.yaml>`_ for all configurable options.

Some things like custom handling of non standard post types is not fully configurable through the config file. You might have to modify the `source code <https://github.com/thomasf/exitwp/blob/master/exitwp.py>`_ to add custom parsing behaviour.

Known issues
============
 * Target file names are some times less than optimal.
 * Rewriting of image/attachment links if they are downloaded would be a good feature
 * There will probably be issues when migrating non utf-8 encoded wordpress dump files (if they exist).

Other Tools
===========
 * A Gist to convert WP-Footnotes style footnotes to PHP Markdown Extra style footnotes: https://gist.github.com/1246047
