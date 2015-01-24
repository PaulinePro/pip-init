import os
from string import Template
from subprocess import Popen, PIPE


# define setup.py template
setup_file = Template('''import os
from setuptools import setup
from pip.req import parse_requirements
from pip.exceptions import InstallationError

try:
    requirements = parse_requirements("requirements.txt")
    install_requires = [str(r.req) for r in requirements]
except InstallationError:
    install_requires = []


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
${lines}    install_requires=install_requires,
    long_description=read('README.md')
)''')


def git_config(key):
    '''Get git config datas.'''
    # run git config --global <key> to get git config value
    p = Popen(['git', 'config', '--global', key], stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()

    # turn stdout into unicode and strip it
    output = output.decode('utf-8').strip()

    return output


def main():
    # define setup fields
    fields = ['name', 'version', 'author', 'author_email', 'description',
              'license', 'keywords', 'url', 'packages', 'entry_points']
    # define default value
    defaults = {
        'name': os.path.relpath('.', '..'),
        'version': '1.0.0',
        'license': 'MIT',
        'author': git_config('user.name'),
        'author_email': git_config('user.email'),
        'packages': 'package-name',
        'entry_points': 'command=package-name:main',
    }
    # save results here
    values = []

    # iterate through each field
    for f in fields:
        if f in defaults:
            # if field has default value, appends default value after field
            result = input('{}: ({}) '.format(f, defaults[f]))

            # if user doesn't enter anything, set result as default value
            if not result:
                result = defaults[f]
        else:
            # if field has no default value, just show the field
            result = input('{}: '.format(f))

        # append result into values
        values.append(result)

    # combine all the fields and values into one string
    lines = ''
    for field, value in zip(fields, values):
        if field == 'packages':
            # if value equals to default value, then we should ignore package
            if value == 'package-name':
                continue

            # compile package names as a string
            lines += '    {}=[{}],\n'.format(
                field,
                ', '.join(['\'{}\''.format(s) for s in value.split()]))
        elif field == 'entry_points':
            # if value equals to default value, then we should ignore it
            if value == 'command=package-name:main':
                continue

            # append entry_point into lines
            console_scripts = '''    entry_points={{
        'console_scripts': [
            '{}',
        ],
    }},\n'''
            lines += console_scripts.format(value)
        else:
            # append field and value into lines
            lines += '    {}=\'{}\',\n'.format(field, value)

    # write compiled template into setup.py
    with open('setup.py', 'wb') as f:
        f.write(bytes(setup_file.substitute(lines=lines), 'utf-8'))

if __name__ == '__main__':
    main()
