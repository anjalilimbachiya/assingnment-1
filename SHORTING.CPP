
  //write a program to input a 10 number into an integer arry &short them in asocciated order
#include <iostream.h>
#include <conio.h>
//function declaration//
void inputarray(int,int);
void  sortingarray(int,int);
void displayarray(int,int);
//function defination//

void inputarray(int arr[], int size) {
    for (int i = 0; i < size; i++) {
	cout << "Enter number " << i + 1 << ": ";
	cin >> arr[i];
    }
}
void sortingarray(int arr[], int size)
{
    int temp;
    for (int i = 0; i < size - 1; i++)
{
	for (int j = 0; j < size - i - 1; j++)
{
	    if (arr[j] > arr[j + 1])
{
		temp = arr[j];
		arr[j] = arr[j + 1];
		arr[j + 1] = temp;
	    }
	}
    }
}
void displayarray(int arr[], int size)
{
    cout << "\nSorted array in ascending order:\n";
    for (int i = 0; i < size; i++)
{
	cout << arr[i] << ", ";
}
}


void main()
{

    int arr[10];
     clrscr();

    inputarray(arr, 10);
    sortingarray(arr, 10);
    displayarray(arr, 10);
    getch();
}
