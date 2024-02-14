import sys
import alembic.config


def main():
    '''
    Simple wrapper for alembic CLI.

    Example usage:
        1. alembic revision --autogenerate -m 'Migration message here'
        2. alembic upgrade head
    '''
    alembic.config.main(sys.argv[1:])


if __name__ == '__main__':
    main()
