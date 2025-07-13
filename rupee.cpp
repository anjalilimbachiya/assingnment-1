//13.All users are charged murimin 50 impees. If the total antount of more than 300, then addnional sumcharge 15% is added

#include <iostream.h>
#include <conio.h>
//function declaration//
float calculateBill(int);
//function defination//

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

    if (bill < 50)
    {
        bill = 50;
    }
    if (bill > 300)
    {
        float surcharge = bill * 0.15;
        bill = bill + surcharge;
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
