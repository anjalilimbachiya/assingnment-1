//2.write a program to input a two number and swept them without using a third variable :

#include<iostream.h>
#include<conio.h>

//function declaration//
int getnum();
void swept();

void main()
{
	int no1,no2,answer;
	clrscr();
	no1=getnum();
	no2=getnum();
	cout<<"\nbefore swepping :";
	cout<<"\n no1 is "<<no1 <<"\n no2 is "<<no2;
	swept();
	cout<<"\n after swepping :";
	cout<<"\n no1 is "<<no1 <<"\n no2 is "<<no2;
	getch();

}

//function defination//
int getnum()
{
	int n;
	cout<<"enter a number :" ;
	cin>>n;
	return n;

}
void swept()
{
	int a,b;
	a=a+b;
	b=a-b;
	a=a-b;

}