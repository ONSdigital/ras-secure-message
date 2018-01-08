import os
import pylint.lint

if __name__ == '__main__':
    os.system('flake8 --count --format=pylint')
    pylint.lint.Run(['--output-format=colorized', '--rcfile=.pylintrc', '-j', '0', './secure_message'])
    # pylint.lint.Run(['--errors-only', '--output-format=colorized', '--rcfile=.pylintrc', './secure_message', './tests'])
