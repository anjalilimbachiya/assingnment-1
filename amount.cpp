//13 all the user are charged minimum 50 rupees. if the total amountis more than 300, than additional surcharge 15% is added
#include <iostream.h>
#include <conio.h>

// Function declaration
float calculateBill(int units);

// Function definition
float calculateBill(int units)
{
    float bill;

    if (units <= 100)
        bill = units * 0.60;
    else if (units <= 300)
        bill = 100 * 0.60 + (units - 100) * 0.80;
    else
        bill = 100 * 0.60 + 200 * 0.80 + (units - 300) * 0.90;

    if (bill < 50)
        bill = 50;

    if (bill > 300)
        bill = bill + (bill * 0.15);

    return bill;
}

void main()
{
    int units;
    float total;

    clrscr();

    cout << "Enter units consumed: ";
    cin >> units;

    total = calculateBill(units);

    cout << "\nTotal bill = Rs. " << total;

    getch();
}
