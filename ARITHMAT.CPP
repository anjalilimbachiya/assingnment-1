// Write a program to perform all the arathmetic opration :
// Input the number from the user

#include<iostream.h>
#include<conio.h>

///function declaration ://
int getnum();
int add(int,int);
int sub(int,int);
int mul(int,int);
int div(int,int);

void main()
{
	int no1,no2,answer;
	clrscr();
	no1=getnum();
	no2=getnum();
	answer=add(no1,no2);
	cout<<"\n substraction answer:" ;
	cout<<answer;
	answer=sub(no1,no2);
	cout<<"\n substraction answer:" ;
	cout<<answer;
	answer=mul(no1,no2);
	cout<<"\n substraction answer:" ;
	cout<<answer;
	answer=div(no1,no2);
	cout<<"\n substraction answer:" ;
	cout<<answer;
	getch();



}
//function defination ://

int getnum()
{
	int n;
	cout<<"Enter a number : ";
	cin>>n;
	return n;
}

int add(int a,int b)
{
	int ans;
	ans=a+b;
	return ans;
}

int sub(int a,int b)
{
	int ans;
	ans=a-b;
	return ans;
}

int mul(int a,int b)
{
	int ans;
	ans=a*b;
	return ans;
}

int div(int a,int b)
{
	int ans;
	ans=a/b;
	return ans;
}



