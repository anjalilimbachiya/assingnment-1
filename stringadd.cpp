//11. Write a C++ program to perform the following operations using function overloading with return type: 
//(a). Addition of two strings (concatenation) (b). Addition of two numbers

#include<iostream.h>
#include<conio.h>
#include<string.h>
int add(int, int);
char* add(char[], char[]);

int add(int a, int b)
{
	return a + b;
}
char* add(char str1[], char str2[])
{
	static char result[200];
	int i = 0, j = 0;

	// Copy str1 into result
	while (str1[i] != '\0')
	{
		result[i] = str1[i];
		i++;
	}

	// Append str2 into result
	while (str2[j] != '\0')
	{
		result[i] = str2[j];
		i++;
		j++;
	}
	result[i] = '\0';  // Null-terminate the string
	return result;
}

void main()
{
	clrscr();

	int x = 5, y = 10;
	char str1[100] = "Hello, ";
	char str2[100] = "World!";

	// Integer addition
	int sum = add(x, y);
	cout << "Sum of " << x << " and " << y << " is: " << sum << endl;

	// String concatenation
	char* combined = add(str1, str2);
	cout << "Concatenated string: " << combined << endl;

	getch();
}
