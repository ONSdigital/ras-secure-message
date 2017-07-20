import pylint.lint

if __name__ == '__main__':
    # pylint.lint.something(__file__, justerrors=True)
    # now continue with unit testing
    pylint.lint.Run(['--errors-only', './app', './tests'])
