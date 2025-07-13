//12. A electricity board charges the following rates to domestic users to discourage large consumption of energy:
//For the first 100 units: 60P per unit
//2. For next 200 units: 80P per und
//3. Beyond 300 uniter: 90P per unt

#include <iostream.h>
#include <conio.h>
//function declaration//
float calculateBill(int);
//function defination///

float calculateBill(int units)
{
    float bill = 0.0;

    if (units <= 100)
    {
        bill = units * 0.60;
    }
    else if (units <= 300)
    {
        bill = 100 * 0.60 + (units - 100) * 0.80;
    }
    else
    {
        bill = 100 * 0.60 + 200 * 0.80 + (units - 300) * 0.90;
    }

    return bill;
}

void main()
{
	int units;
        float total;
        clrscr();
    	cout << "Enter total units consumed: ";
    	cin >> units;
    	total = calculateBill(units);
   	cout << "\nTotal Bill for " << units << " units = Rs. " << total;

    	getch();
}

