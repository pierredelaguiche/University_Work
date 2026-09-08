#include <limits.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

/*
Begin of general documentation:
Create functions to: calculate the output and manage the recursive function for
calculating the output. Said recursive function must also be completed. Another
function is created to close the arrays if needed. The main loop is used to get
the input while checking the limits (as to avoid edge cases). This is done
through two arrays allocated after first part of input is read. said arrays are
then allocated their values, and the calculating functions is then passed all of
these variables. The function now calles for each possible loan the recursive
function, and updates the best possible loan if it encounters a better one
sequentially. It also checks (in the recursive function) if the loan is
completable or impossible. Due to many arguments being passed around, a pointer
was used to update a buffer within the recursive function. This was strongly
aided by
https://stackoverflow.com/questions/2620146/how-do-i-return-multiple-values-from-a-function-in-c
. Rest of code knowledge was learned from lectures, geeksforgeeks, w3schools,
and stackoverflow, not copied. End of general documentation. Step by step
comments can be found next to their respective lines.
*/

void closure(int *interest,
             int *monthly_payment) { // function used at exit states as not to
                                     // keep the arrays in memory
  free(interest);
  free(monthly_payment);
}

int recursive(
    int borrowed_amount, float decimal_interest_i, int monthly_payment_i,
    int *interest, int *monthly_payment, int months_counter,
    int *best_buffer) { // pointers reference for updating the best_buffer
                        // without returning the value (and compensating for the
                        // excess money paid when payment is larger than owed):
                        // https://stackoverflow.com/questions/2620146/how-do-i-return-multiple-values-from-a-function-in-c
                        // . This function is recursive and used as a 'loop' to
                        // get the amount of months and leftover payments (with
                        // said pointer)
  int after_payment =
      borrowed_amount -
      monthly_payment_i; // assigning a variable to the amount after payment as
                         // not to reduntantly make calculations
  int buffer = 0;        // buffer set to 0 as to avoid undefined behaviour

  if (after_payment <=
      0) { // checking if payment was completed and returning months as well as
           // adding the payment difference to the address of best_buffer
           // (variable to compare with best_total or the least expensive
           // payment plan)
    *best_buffer = after_payment;
    return ++months_counter;
  }

  buffer =
      floor(after_payment *
            decimal_interest_i); // calculate the interest and use floor() to
                                 // round down and assign value to buffer
  if (buffer >=
      monthly_payment_i) { // if buffer (only the interest increment) is bigger
                           // or equal to the payments, loan will not be paid
                           // off ever. return 0 instead of exiting, other cases
                           // might be valid
    return 0;
  }

  borrowed_amount =
      after_payment + buffer; // re-assign borrowed amount to recursively call
                              // the function with different parameters
  return recursive(borrowed_amount, decimal_interest_i, monthly_payment_i,
                   interest, monthly_payment, ++months_counter,
                   best_buffer); // recursively calling the function (sorry for
                                 // the rediculous amount of variables, not
                                 // super stack/memory efficient)
}

void interest_func(
    int borrowed_amount, int n_of_loans, int *interest,
    int *monthly_payment) { // function to calculate best loan option. It cycles
                            // through every option and replaces the according
                            // best values in memory
  int best_total = INT_MAX; // since the lowest total is best, this var is
                            // initiated with INT_MAX
  int best_buffer = 0;
  int best_n_months = 0;
  int months_buffer = 0;
  int j = 0; // counter for array indexes

  while (n_of_loans > 0) {
    int i = 0; // counter for recusive month counter (therefore outside function
               // and inside while loop)

    months_buffer = recursive(
        borrowed_amount, (float)(interest[j] / 100.0), monthly_payment[j],
        interest, monthly_payment, i,
        &best_buffer); // call function, assing months_buffer with return value,
                       // and pass indexed array (and arrays to free if
                       // necessary, although easily avoidable if needed) and
                       // interest formated for future equation (float and in
                       // decimal not percentage)
    best_buffer +=
        (months_buffer *
         monthly_payment[j]); // assign best buffer by multiplying months and
                              // payments with best_buffer already having been
                              // adjusted to take into account the lesser final
                              // payment through pointers

    if (best_total > best_buffer && best_buffer != 0 &&
        months_buffer !=
            0) { // update best options if necessary, include best months in
                 // elif statement to avoid clashes. Check (twice for the
                 // months) that the buffers are not equal to 0. If they are,
                 // ignore the buffers.
      best_total = best_buffer;
      best_n_months = months_buffer;
    } else if (best_total == best_buffer && best_n_months > months_buffer &&
               months_buffer != 0) {
      best_n_months = months_buffer;
    }
    n_of_loans--; // increment all counters
    j++;
  }
  if (best_total ==
      INT_MAX) { // if the best_total was not readjusted print impossible and
                 // exit accordingly. Else print the result
    printf("impossible");
    closure(interest, monthly_payment);
    exit(EXIT_SUCCESS);
  } else {
    printf("%d %d", best_total, best_n_months);
  }
  return;
}

int main() {
  int borrowed_amount, n_of_loans,
      i; // initiate all ints in main func as well as array counter
  if ((scanf("%d %d", &borrowed_amount, &n_of_loans)) != 2 ||
      1000000 < borrowed_amount || borrowed_amount < 1 || 20 < n_of_loans ||
      n_of_loans < 1) { // check for the input limits, exit properly if not
    printf("impossible");
    exit(EXIT_SUCCESS);
  }

  int *interest = malloc(
      sizeof(int) * n_of_loans); // initiate arrays according to previous input
  int *monthly_payment = malloc(sizeof(int) * n_of_loans);

  if (interest == NULL ||
      monthly_payment == NULL) { // check that the memory allocation was indeed
                                 // successful. Exit if not
    printf("Memory allocation unsuccessful.\n");
    closure(interest, monthly_payment);
    exit(EXIT_FAILURE);
  }

  for (i = 0; i < n_of_loans;
       i++) { // read all values of array through for loop and use if to both
              // assign values and check if input gives error. Exit
              // appropriately if not
    if ((scanf("%d %d", &interest[i], &monthly_payment[i]) != 2) ||
        1000 < interest[i] || interest[i] < 0 || 1000000 < monthly_payment[i] ||
        monthly_payment[i] < 0) {
      printf("impossible");
      closure(interest, monthly_payment);
      exit(EXIT_SUCCESS);
    }
  }

  interest_func(borrowed_amount, n_of_loans, interest,
                monthly_payment); // call function for getting, printing, and
                                  // managing best loans
  closure(interest, monthly_payment); // close all arrays before exiting
}