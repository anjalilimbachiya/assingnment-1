// 3 : write a program to find a meximum of 3 input number :

#include<iostream.h>
#include<conio.h>
//function declaration//

int max(int,int,int);

void main()
{
	int no1,no2,no3,maximum;
	clrscr();
	cout<<"\n Enter a three number :";
	cin>>no1>>no2>>no3;
	maximum=max(no1,no2,no3);
	getch();
}
int max(int a,int b,int c)
{
	int max;

	if(a>b && a>c)
	{
		cout<<" no1 is maximum" ;
	}
	else if(b>a && b>c)
	{
		cout<<"no2 is maximum";

	}
	else if(c>a && c>b)
	{
		cout<<"no3 is maximum";
	}
	else
	{
		cout<<"bought are equal";
	}
	return max;





}