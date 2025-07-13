#include<iostream.h>
#include<conio.h>
void printMessage(int);

void main()
{
      clrscr();
      int n;
      cout<<"enter a number:";
      cin>>n;
      printMessage(n);
      getch();
}
void printMessage(int count)
{
	for(int i=0;i<count;i++)
	{
		cout<<"Well Done"<<endl;
	}
}