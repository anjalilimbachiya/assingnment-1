#include <iostream.h>
#include <conio.h>
//function declaration
float temprature(float);

//function defination//
float temprature(float c)
{
	float r;
        r=(c* 9.0 / 5.0) + 32;
	return r;
}

void main()
{
    float c,f;
    clrscr();
    cout << "Enter temperature in Celsius: ";
    cin >> c;
    f=temprature(c);
    cout << "Temperature in Fahrenheit: " <<f;
    getch();
}
