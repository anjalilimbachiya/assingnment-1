//9 write a program suing string function :
#include <iostream.h>
#include <conio.h>
#include <string.h> 

// Function declarations//
void copyString(char[], char[]); 
int getStringLength(char[]); 
int compareStrings(char[], char[]);
void copyString(char d[], char src[]) {
    strcpy(d, src);
}
int getStringLength(char str[]) {
    return strlen(str);
}
int compareStrings(char str1[], char str2[]) {
    return strcmp(str1, str2);
}

void main()
{
    clrscr(); 
    char str1[50], str2[50], str3[50];
    int length, result;

    cout << "Enter first string: ";
    cin >> str1;

    cout << "Enter second string: ";
    cin >> str2;

    copyString(str3, str1);
    cout << "\nCopied str1 to: " << str3;

    length = getStringLength(str1);
    cout << "\nLength of str1: " << length;

    result = compareStrings(str1, str2);
    if(result == 0)
        cout << "\nstr1 and str2 are equal.";
    else if(result > 0)
        cout << "\nstr1 is greater than str2.";
    else
        cout << "\nstr1 is less than str2.";

    getch(); 
}
