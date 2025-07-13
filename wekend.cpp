#include <iostream.h>
#include <conio.h>

// Declare enumeration for weekdays
enum Weekdays {
    Sunday = 1,
    Monday,
    Tuesday,
    Wednesday,
    Thursday,
    Friday,
    Saturday
};

// Function to print the day name
void printDayName(int dayNumber) {
    switch(dayNumber) {
        case Sunday:
            cout << "Sunday";
            break;
        case Monday:
            cout << "Monday";
            break;
        case Tuesday:
            cout << "Tuesday";
            break;
        case Wednesday:
            cout << "Wednesday";
            break;
        case Thursday:
            cout << "Thursday";
            break;
        case Friday:
            cout << "Friday";
            break;
        case Saturday:
            cout << "Saturday";
            break;
        default:
            cout << "Invalid day number. Please enter between 1 and 7.";
    }
}

void main() {
    clrscr(); // Clear the screen
    int dayNumber;

    cout << "Enter a number (1 to 7): ";
    cin >> dayNumber;

    cout << "The day is: ";
    printDayName(dayNumber);

    getch();
}
