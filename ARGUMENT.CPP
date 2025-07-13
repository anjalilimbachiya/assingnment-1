#include<iostream.h>
#include<conio.h>
int multiply(int a, int b=2)
{
	return a*b;
}
void display(const char str[])
{
	cout<<"you entered:"<<str<<endl;
}
void main()
{
	clrscr();

	int result1 = multiply(5);
	int result2 = multiply(5, 3);

	cout<<"result with default argument(5*2):"<<result1<<endl;
	cin>>result1;
	cout<<"result with both argument(5*3):"<<result2<<endl;
	cin>>result2;

	char message[]="Hello, Turbo C++!";
	display(message);
	getch();

}

