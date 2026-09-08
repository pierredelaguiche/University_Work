#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

/*
Begin of general documentation:
Create a function for: checking if the message is matched forwards, checking if
the message is matched backwards, get str length, check 1 character case and one
to close strings if necessary. Most main loop code is for the input and
allocation of memory up to necessary boundaries. Use loops for checking
messages, with one counter for the message and one for the key. Final check and
main loop logic is done with for loops and some 'else' logic as to isolate edge
cases, functions are called within those. Error handling was also put in place,
and during memory allocation too with some help and tweaks from
https://mkyong.com/c/how-to-handle-unknow-size-user-input-in-c/ . Rest of code
knowledge was learned from lectures, geeksforgeeks, w3schools, and
stackoverflow, not copied.
End of general documentation. Step by step comments can be found next to their
respective lines.
*/

void closure(char *str_1, char *str_2) { // function used at exit states as not
                                         // to keep the arrays in memory
  free(str_1);
  free(str_2);
}

int get_len_str(char const *str) { // function to get the length of a string
  int i = 0;                       // counter set to 0
  while (str[i] != 0) {
    i++;
  }           // iterate through the string until the closing character
  return --i; // subtract 1 from counter before passing argument since we're
              // comaring against indexes and starting at 0
}

bool check_single_character(
    char const *str,
    char const *key) { // because of the way my code is written, a single
                       // character comparison has to be implemented
  if (get_len_str(str) == 0 && get_len_str(key) == 0 && str[0] == key[0]) {
    return true;
  } // check the three conditions; both strings have length 1 (0 due to my
    // length function) and that both characters are the same)
  else {
    return false;
  }
}

bool check_forwards(char const *str,
                    char const *key) { // passing the strings as constants to
                                       // avoid tampering with the input
  int i = 0;                           // counter for the string input set to 0
  int j = 0;                           // counter for the key set to 0
  int const str_len = get_len_str(
      str); // str_len set to the length of the string to use in loop
  int const key_len =
      get_len_str(key); // key_len set to the length of the key to use in loop
  while (i < str_len) { // while the string counter is smaller than the string
                        // input length
    if (str[i++] == key[j]) {
      j++;
    } // if the string items are equal, move to next character in key
    if (j >= key_len) { // if the whole key got iterated over, return true (use
                        // bigger-than to avoid edge-case-bugs)
      return true;
    }
  }
  return false; // else, return false
}

bool check_backwards(char const *str,
                     char const *key) { // passing the strings as constants to
                                        // avoid tampering with the input
  int i = 0;                            // counter for the input set to 0
  int j = get_len_str(key); // counter for the key set to the length of the key
  int const str_len = get_len_str(
      str); // str_len set to the length of the string to use in loop
  while (i < str_len) { // while the string counter is smaller than the string
                        // input length
    if (str[i++] == key[j]) {
      j--;
    } // if the string items are equal, move to previous character in key
    if (j <= 1) { // if the whole key got iterated over, return true (use
                  // smaller-than to avoid edge-case-bugs)
      return true;
    }
  }
  return false; // else, return false
}

int main() { // input and memory allocation management was aided (but not
             // copied) by
             // https://mkyong.com/c/how-to-handle-unknow-size-user-input-in-c/
  unsigned const int max_len_str_1 = 128; // declare max length of string 1
  unsigned const int max_len_str_2 = 128; // declare max length of string 2
  unsigned int len_str_1, len_str_2; // declare length variable of the strings

  char *str_1 = malloc(max_len_str_1); // allocate memory for both strings
  char *str_2 = malloc(max_len_str_2);

  len_str_1 = max_len_str_1; // set the current length as the maximum length
  len_str_2 = max_len_str_2;

  if (str_1 == NULL || str_2 == NULL) { // check that the memory allocation was
                                        // indeed successful. Exit if not
    printf("Memory allocation unsuccessful.\n");
    closure(str_1, str_2);
    exit(EXIT_FAILURE);
  }

  int input =
      EOF;   // set an input buffer and declare as EOF to help with misinputs
  int i = 0; // incremental variable for indexing onto the array

  while (
      (input = getchar()) != '\n' &&
      (input !=
       EOF)) { // declare input as getchar() and check that the user hasn't
               // entered a terminating/invalid character. Code tweaked from:
               // https://mkyong.com/c/how-to-handle-unknow-size-user-input-in-c/
    str_1[i++] =
        (char)tolower(input); // append the input onto the string and increment
                              // (after the fact) the indexing variable

    if (i ==
        len_str_1) { // check if the current index and the size of the array are
                     // equal. Code tweaked from:
                     // https://mkyong.com/c/how-to-handle-unknow-size-user-input-in-c/
      if (len_str_1 < 9871) {
        len_str_1 += max_len_str_1;
        str_1 = realloc(str_1,
                        len_str_1); // reallocate the array and adjust the size
      } // increment by 128 the variable of the length of the array while
        // checking it wont go over 10000 (line 68-79 are in charge to checking
        // for the 10'000 character limit).
      else {
        if (len_str_1 < 10000) {
          str_1 = realloc(str_1, 10000);
        } else {
          printf("Message cannot be over 10'000 characters.\n");
          closure(str_1,
                  str_2);     // free arrays and pointers if string is too long
          exit(EXIT_SUCCESS); // exit the program with no errors
        }
      }
      if (str_1 == NULL) { // check that the array was successfully allocated.
                           // Exit with fail if not
        printf("Memory allocation unsuccessful.\n");
        closure(str_1, str_2);
        exit(EXIT_FAILURE);
      }
    }
  }
  str_1[i] = '\0'; // terminate the string by appending the string-terminator

  // repeat for str_2 (same code, diferent variables (str_2 instead as str_1)).
  input = EOF; // and reset the indexing and input variables
  i = 0;

  while ((input = getchar()) != '\n' && (input != EOF)) {
    str_2[i++] = (char)tolower(input);

    if (i == len_str_2) {
      if (len_str_2 < 9871) {
        len_str_2 += max_len_str_2;
        str_2 = realloc(str_2, len_str_2);
      } else {
        if (len_str_2 < 10000) {
          str_2 = realloc(str_2, 10000);
        } else {
          printf("Message cannot be over 10'000 characters.\n");
          closure(str_1, str_2);
          exit(EXIT_SUCCESS);
        }
      }
      if (str_2 == NULL) {
        printf("Memory allocation unsuccessful.\n");
        closure(str_1, str_2);
        exit(EXIT_FAILURE);
      }
    }
  }
  str_2[i] = '\0';

  if (get_len_str(str_1) == -1 ||
      get_len_str(str_2) ==
          -1) { // checking that both strings have 1 or more characters
    printf(
        "String and key must both have at least one character.\n"); // print for
                                                                    // the user
    closure(str_1, str_2); // free strings and pointers
    exit(EXIT_SUCCESS);    // exit with no error
  }

  if (check_forwards(str_1, str_2) ==
      true) { // using the functions defined at the top, we sequentially check
              // fowards, backwards, and for the single character edge-case
              // before returning a 'no' if no match for the key was found.
    printf("yes\n");
  } else {
    if (check_backwards(str_1, str_2) == true) {
      printf("yes\n");
    } else {
      if (check_single_character(str_1, str_2) == true) {
        printf("yes\n");
      } else {
        printf("no\n");
      }
    }
  }

  closure(str_1, str_2); // free up arrays and hanging pointers as good practice
}