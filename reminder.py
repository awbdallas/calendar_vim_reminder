import calendarvim
import sys


def main():
    filepath = sys.argv[1]
    print(filepath)
    holding = calendarvim.CalendarVimParser(filepath)
    result = holding.load_calendar()

    for calendar in result:
        print(calendar.events)

if __name__ == '__main__':
    main()
