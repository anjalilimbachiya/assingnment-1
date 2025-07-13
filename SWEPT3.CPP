//7 write a prgram using reference variable :
#include<iostream.h>
#include<conio.h>
//function declaration//
void swept(int,int);
//function defination//
void swept(int a,int b)
{
	int temp;
	temp =a;
	a=b;
	b=temp;
}
int main()
{
	int no1,no2,r;
	clrscr();
	cout<<"Enter two number : " ;
	cin>>no1>>no2;
	cout<<"\n before swepping no1 and no 2 : " <<no1 <<"," <<no2;
	swept(no1,no2);
	cout<<"\n after swepping no1 and no2 :" <<no1<<","<<no2;
	getch();
	return 0;
}
